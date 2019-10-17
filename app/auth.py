from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request
from flask import session
from flask import jsonify
from functools import wraps

from helpers import get_db

import bcrypt


auth = Blueprint('auth', __name__)


def loggedin(func):
    ''' Raise 403 error if user is not logged in '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            abort(403)
        return func(*args, **kwargs)
    return wrapper


@auth.route('/', methods=['GET'])
def index():
    if 'user' not in session:
        return render_template('login.html', title='Login', hide_navbar=True)
    else:
        return render_template('home.html',
                               heading='My Dashboard', title='My Dashboard')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html',
                               title='Register', hide_navbar=True)

    email = request.form.get('email', None)
    password = request.form.get('password', None)
    if email is None or len(email) is 0:
        return jsonify({'status': 'fail',
                        'message': 'email is blank'})
    if password is None or len(password) is 0:
        return jsonify({'status': 'fail',
                        'message': 'password is blank'})

    conn = get_db()
    res = conn.execute('SELECT email FROM users WHERE email = ?', [email])
    if res.fetchone():
        conn.close()
        return jsonify({'status': 'fail',
                        'message': 'Email has already been registered!'})
    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(f'Registering user {email} with hashed password {hashed_pass}')
    conn.execute('INSERT INTO users (email, password) VALUES (?, ?)',
                 [email, hashed_pass])
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Login', hide_navbar=True)

    email = request.form.get('email', None)
    password = request.form.get('password', None)
    if email is None or len(email) is 0:
        return jsonify({'status': 'fail',
                        'message': 'email is blank'})
    if password is None or len(password) is 0:
        return jsonify({'status': 'fail',
                        'message': 'password is blank'})

    conn = get_db()
    res = conn.execute('SELECT password FROM users WHERE email = ?', [email])
    hashed_password = res.fetchone()
    if not hashed_password:
        conn.close()
        return jsonify({'status': 'fail',
                        'message': 'Unknown email!'})
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password[0]):
        return jsonify({'status': 'fail',
                        'message': 'Wrong password!'})
    print('Loging in user')
    session['user'] = email
    conn.close()
    return jsonify({'status': 'ok'})


@auth.route('/home', methods=['GET'])
@loggedin
def home():
    if request.method == 'GET':
        return render_template('home.html',
                               heading='My Dashboard', title='My Dashboard')
