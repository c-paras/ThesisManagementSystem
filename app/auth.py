from flask import abort
from flask import Blueprint
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from datetime import datetime
from enum import Enum
from functools import wraps

from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload
from app.helpers import error
from app.helpers import get_fields
from app.helpers import send_email
from app.queries import queries
from app.update_accounts import enroll_user
from app.update_accounts import get_all_account_types

import bcrypt
import re
import uuid

import config


auth = Blueprint('auth', __name__)


# user privillege levels
class UserRole(Enum):
    PUBLIC = 0        # default user type - can only search for topics
    STUDENT = 1       # students are promoted from public type
    STAFF = 2         # supervisor or assessor
    COURSE_ADMIN = 3  # thesis admins
    SUPER_ADMIN = 4   # unused; possibly needed in future


def is_at_least_role(role):
    ''' Check if user's role type is sufficient for access '''
    if 'acc_type' not in session:
        return False
    actual_role = session['acc_type']
    r = role.value
    if role == UserRole.PUBLIC or actual_role == 'super_admin':
        return True
    elif actual_role == 'student' and r <= UserRole.STUDENT.value:
        return True
    elif actual_role == 'supervisor' and r <= UserRole.STAFF.value:
        return True
    elif actual_role == 'course_admin' and r <= UserRole.COURSE_ADMIN.value:
        return True
    else:
        return False


def at_least_role(role):
    ''' Raise 403 error if user is trying to access a disallowed route '''
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('auth.login'))
            if not is_at_least_role(role):
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper


def allowed_file_access(filename):
    ''' Check if a file access should be permitted '''

    if 'user' not in session:
        raise KeyError('Not logged in')
    if not is_at_least_role(UserRole.STUDENT):
        # public users shouldn't have access to any file uploads
        return False
    if is_at_least_role(UserRole.STAFF):
        # allow staff to have access to anything
        return True

    # students should only have access to files they have submitted
    # or files in tasks within courses they are part of
    # or material files within courses they are part of
    # as long as the task and/or material is marked as visible

    try:
        name = FileUpload(filename=filename).get_name()
    except LookupError as e:
        if config.DEBUG:
            print(f'Request file: {e}')
        abort(404)
    db.connect()
    submitted_file = db.select_columns('submissions', ['path'],
                                       ['student', 'path'],
                                       [session['id'], name])
    task_files = queries.get_allowed_task_attachments(session['id'])
    materials = queries.get_allowed_material_attachments(session['id'])
    db.close()
    if submitted_file or (task_files and name in task_files) or \
       (materials and name in materials):
        return True
    else:
        return False


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html',
                               title='Register', hide_navbar=True)

    try:
        fields = ['email', 'password', 'confirm-password']
        email, password, confirm = get_fields(request.form, fields)
    except ValueError as e:
        return e.args[0]

    if not re.match(config.EMAIL_FORMAT, email):
        return error(
            f'Invalid email format!<br>{config.EMAIL_FORMAT_ERROR}', 'email')

    db.connect()
    res = db.select_columns('users', ['email', 'date_created', 'confirm_code'],
                            ['email'], [email])

    now = datetime.now().timestamp()
    if len(res):
        if res[0][2] != '' and res[0][1] + config.ACCOUNT_EXPIRY < now:
            # expire unactivated accounts every 24 hours
            db.delete_rows('users', ['email'], [email])
        else:
            db.close()
            return error('This email has already been registered!', 'email')

    if len(password) < 8:
        msg = 'Password must be at least 8 characters long!'
        db.close()
        return error(msg, 'password')

    if password != confirm:
        db.close()
        return error('Passwords do not match!', 'confirm-password')

    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    name = email.split('@')[0]

    # get the id for a public account
    acc_type = db.select_columns('account_types',
                                 ['id'], ['name'], ['public'])

    confirm_code = uuid.uuid1()
    activation_link = url_for('.confirm', user=name,
                              confirm_code=confirm_code, _external=True)
    send_email(to=email, name=email, subject='Confirm Account Registration',
               messages=[
                   'You recently registered for an account on TMS.',
                   'To activiate your account, click ' +
                   f'<a href="{activation_link}">here</a>.',
                   'This link will expire in 24 hours.'
               ])

    db.insert_single(
        'users',
        [name, hashed_pass, email, acc_type[0][0], str(confirm_code), now],
        ['name', 'password', 'email', 'account_type', 'confirm_code',
         'date_created']
    )
    db.close()
    return jsonify({'status': 'ok'})


@auth.route('/confirm', methods=['GET'])
def confirm():
    confirm_code = request.args.get('confirm_code', '')
    user = request.args.get('user', '')
    db.connect()

    # get the user's confirm code & creation date
    res = db.select_columns(
        'users', ['confirm_code', 'date_created', 'email', 'id'],
        ['name'], [user]
    )

    expired = False
    now = datetime.now().timestamp()
    if len(res) and res[0][1] + config.ACCOUNT_EXPIRY < now:
        expired = True  # expire unactivated accounts every 24 hours
        db.delete_rows('users', ['name'], [user])
        flash('This activation link has expired!<br>' +
              'You must register your account again.', 'error')
    if not expired and len(res) and confirm_code == res[0][0]:
        # clear confirm code to "mark" account as activated
        user_id = res[0][3]
        res = db.select_columns(
            'update_account_types',
            ['id', 'new_name', 'account_type', 'course_offering'],
            ['email'], [res[0][2]]
        )
        if len(res) > 0:
            db.update_rows(
                'users', ['', res[0][1], res[0][2]],
                ['confirm_code', 'name', 'account_type'],
                ['name'], [user]
            )
            if res[0][3] is not None:
                account_types = get_all_account_types()
                course_role = 'staff'
                if account_types['student'] == res[0][2]:
                    course_role = 'student'
                course_role_id = db.select_columns(
                    'course_roles', ['id'], ['name'], [course_role]
                )
                enroll_user(user_id, res[0][3], course_role_id[0][0])
            db.delete_rows('update_account_types', ['id'], [res[0][0]])
        else:
            db.update_rows('users', [''], ['confirm_code'], ['name'], [user])
        flash('Account activated! You can now log in.', 'success')
    db.close()
    return redirect(url_for('.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        # if already logged in, redirect to home page
        return redirect(url_for('home.dashboard'))
    if request.method == 'GET':
        return render_template('login.html', title='Login', hide_navbar=True)

    try:
        email, password = get_fields(request.form, ['email', 'password'])
    except ValueError as e:
        return e.args[0]

    db.connect()
    res = db.select_columns('users',
                            ['password', 'account_type',
                             'id', 'name', 'confirm_code'],
                            ['email'],
                            [email])

    if not len(res):
        db.close()
        return error('Unknown email!', 'email')
    hashed_password = res[0]
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password[0]):
        db.close()
        return error('Incorrect password!', 'password')
    if res[0][4] != '':
        db.close()
        return error('You must first confirm your account!')

    # get the current user's account type
    acc_type = db.select_columns('account_types',
                                 ['name'],
                                 ['id'],
                                 [res[0][1]])[0][0]

    session['user'] = email
    session['name'] = res[0][3]
    session['id'] = res[0][2]
    session['acc_type'] = acc_type
    db.close()
    return jsonify({'status': 'ok'})


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('.login'))
