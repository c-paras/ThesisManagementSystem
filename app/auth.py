from flask import Blueprint
from flask import render_template
from flask import request
from flask import jsonify

from helpers import get_db

import bcrypt


auth = Blueprint('auth', __name__)


@auth.route('/', methods=['GET'])
def index():  # TODO
    return render_template('login.html', title='Login', hide_navbar=True)


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
def login():  # TODO
    if request.method == 'GET':
        return render_template('login.html', title='Login', hide_navbar=True)


@auth.route('/home', methods=['GET'])
def home():  # TODO
    if request.method == 'GET':
        return render_template('home.html',
                               heading='My Dashboard', title='My Dashboard')
