from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import jsonify
from flask import url_for
from functools import wraps

from app.helpers import error
from app.helpers import get_fields
from app.db_manager import sqliteManager as db

import re
import bcrypt

import config


auth = Blueprint('auth', __name__)


def loggedin(func):
    ''' Raise 403 error if user is not logged in '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            abort(403)
        return func(*args, **kwargs)
    return wrapper


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html',
                               title='Register', hide_navbar=True)

    try:
        fields = ['email', 'password', 'confirm-password', 'registration-key']
        email, password, confirm, key = get_fields(request.form, fields)
    except Exception as e:
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

    if key != config.REGISTRATION_KEY:
        db.close()
        return error('Invalid registration key!')

    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    name = email.split('@')[0]

    # get the id for a student account
    acc_type = db.select_columns('account_types',
                                 ['id'],
                                 ['name'],
                                 ['student'])

    db.insert_single(
        'users',
        [name, hashed_pass, email, acc_type[0][0]],
        ['name', 'password', 'email', 'account_type']
    )
    db.close()
    return jsonify({'status': 'ok'})


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Login', hide_navbar=True)

    try:
        email, password = get_fields(request.form, ['email', 'password'])
    except Exception as e:
        return e.args

    db.connect()
    res = db.select_columns('users',
                            ['password', 'account_type'],
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
    session['acc_type'] = acc_type
    db.close()
    return jsonify({'status': 'ok'})


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user' in session:
        del session['user']
    if 'acc_type' in session:
        del session['acc_type']
    return redirect(url_for('.login'))
