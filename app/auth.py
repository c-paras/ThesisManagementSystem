from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import jsonify
from flask import url_for

from enum import Enum
from functools import wraps

from app.helpers import error
from app.helpers import get_fields
from app.helpers import send_email
from app.db_manager import sqliteManager as db

import re
import bcrypt
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


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html',
                               title='Register', hide_navbar=True)

    try:
        fields = ['email', 'password', 'confirm-password']
        email, password, confirm = get_fields(request.form, fields)
    except ValueError as e:
        return e.args

    if not re.match(config.EMAIL_FORMAT, email):
        return error(f'Invalid email format!<br>{config.EMAIL_FORMAT_ERROR}')

    db.connect()
    res = db.select_columns('users', ['email'], ['email'], [email])
    if len(res):
        db.close()
        return error('Email has already been registered!')

    if len(password) < 8:
        msg = 'Password must be at least 8 characters long!'
        db.close()
        return error(msg)

    if password != confirm:
        db.close()
        return error('Passwords do not match!')

    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    name = email.split('@')[0]

    # get the id for a public account
    acc_type = db.select_columns('account_types',
                                 ['id'],
                                 ['name'],
                                 ['public'])

    confirm_code = uuid.uuid1()
    activation_link = 'TODO'
    send_email(to=email, name='John Smith',
               subject='Confirm Account Registration', messages=[
                   'You recently registered for an account on TMS.',
                   f'To activiate your account, click ' +
                   '<a href="{activation_link}">here</a>.'
               ])

    db.insert_single(
        'users',
        [name, hashed_pass, email, acc_type[0][0], str(confirm_code)],
        ['name', 'password', 'email', 'account_type', 'confirm_code']
    )
    db.close()
    return jsonify({'status': 'ok'})


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
        return e.args

    db.connect()
    res = db.select_columns('users',
                            ['password', 'account_type', 'id', 'name'],
                            ['email'],
                            [email])

    if not len(res):
        db.close()
        return error('Unknown email!')
    hashed_password = res[0]
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password[0]):
        db.close()
        return error('Incorrect password!')

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
