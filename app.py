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
    return render_template('base.html')  # TODO


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

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
                        'message': 'email has already been registered'})
    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(f'Registering user {email} with hashed password {hashed_pass}')
    conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', [email, hashed_pass])
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
