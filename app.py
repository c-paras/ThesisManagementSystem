from flask import Flask, render_template, session, request
from flask import Response, url_for, redirect, g, jsonify
from flask_restful import Resource, Api, reqparse, fields, marshal

import sqlite3
import bcrypt
import config


app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config.DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('login.html', title='Login', hide_navbar=True)


@app.route('/register', methods=['GET', 'POST'])
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Login', hide_navbar=True)


@app.route('/home', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('home.html',
                               heading='My Dashboard', title='My Dashboard')


if __name__ == '__main__':
    if config.DEBUG:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(use_reloader=True, debug=config.DEBUG)
