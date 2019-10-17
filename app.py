from flask import Flask, render_template, session, request
from flask import Response, url_for, redirect, g, jsonify
from flask_restful import Resource, Api, reqparse, fields, marshal

import bcrypt

from db_manager import sqliteManager as db

app = Flask(__name__)



@app.teardown_appcontext
def close_connection(exception):
    db.close(exception)


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

    db.connect()
    res = db.select_columns('users',['email'],['email'],[email])

    if res is not None:
        db.close()
        return jsonify({'status': 'fail',
                        'message': 'email has already been registered'})
    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(f'Registering user {email} with hashed password {hashed_pass}')
    name = email.split('@')[0]
    db.insert_row(
        users,
        [name, hashed_pass, email],
        ['name', 'password', 'email']
    )
    db.close()
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(use_reloader=True, debug=True)
