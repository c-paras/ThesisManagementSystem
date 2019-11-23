from flask import Blueprint
from flask import jsonify
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import render_template

from app.auth import at_least_role
from app.auth import UserRole
from app.db_manager import sqliteManager as db
from app.helpers import error
from app.helpers import get_fields
from app.helpers import send_email

import config
import json
import bcrypt
import re
import uuid


change_password = Blueprint('change_password', __name__)


@change_password.route('/change_password', methods=['POST'])
@at_least_role(UserRole.PUBLIC)
def change_user_password():

    try:
        fields = ['new-password', 'new-confirm-password']
        password, confim_pass = get_fields(request.form, fields)
    except ValueError as e:
        return e.args[0]

    if len(password) < 8:
        return error('Password must be at least 8 characters long!')

    acc_id = session['id']
    hash_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    db.connect()
    db.update_rows('users', [hash_pass], ['password'], ['id'], [acc_id])
    db.close()
    return jsonify({'status': 'ok'})


@change_password.route('/reset_password_req', methods=['POST'])
def reset_request():

    try:
        fields = ['email_reset']
        email = get_fields(request.form, fields)
        email = email[0]
    except ValueError as e:
        return e.args[0]

    if not re.match(config.EMAIL_FORMAT, email):
        return error(f'Invalid email format!<br>{config.EMAIL_FORMAT_ERROR}')

    db.connect()

    res = db.select_columns('users', ['name', 'id'], ['email'], [email])
    if len(res) == 0:
        return jsonify({'status': 'ok'})

    reset_id = str(uuid.uuid1())
    db.connect()
    db.update_rows('users', [reset_id], ['reset_code'],
                   ['id'], [res[0][1]])
    db.close()

    reset_link = url_for('.reset', user=res[0][1],
                         resetID=reset_id, _external=True)
    send_email(to=email, name=res[0][0], subject='Reset Password',
               messages=[
                   'You have submitted a request ' +
                   'to reset your password on TMS.',
                   f'Your account is "{email}".',
                   'click ' +
                   f'<a href="{reset_link}">here</a>' +
                   ' to reset your password'

               ])

    return jsonify({'status': 'ok'})


@change_password.route('/reset_password', methods=['GET', 'POST'])
def reset():
    if request.method == 'GET':
        user_id = request.args.get('user', None)
        reset_id = request.args.get('resetID', None)

        db.connect()
        res = db.select_columns('users', ['id'], ['reset_code'],
                                [reset_id])
        db.close()
        if not len(res) or user_id != str(res[0][0]):
            return redirect(url_for('auth.login'))

        return render_template('reset_password.html',
                               title='Reset Password',
                               hide_navbar=True,
                               user_id=user_id,
                               reset_id=reset_id)

    data = json.loads(request.data)
    user_id = data['user_id']
    reset_id = data['reset_id']
    new_pass = data['new_pass']
    new_confirm = data['new_confirm']

    if len(new_pass) < 8:
        return error('Password must be at least 8 characters long!')

    if new_pass != new_confirm:
        return error('Passwords do not match!')

    db.connect()
    reset_id_test = db.select_columns('users', ['reset_code'],
                                      ['id'], [user_id])[0][0]

    hash_pass = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())

    if reset_id == reset_id_test:

        db.update_rows('users', [hash_pass, ''],
                       ['password', 'reset_code'], ['id'], [user_id])
        db.close()

    else:
        return error('You are not allowed to change this password!')

    return jsonify({'status': 'ok'})
