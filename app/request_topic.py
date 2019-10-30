from flask import Blueprint
from flask import jsonify
from flask import request
from flask import session

from datetime import datetime

from app.auth import UserRole
from app.auth import at_least_role
from app.helpers import error
from app.helpers import get_fields
from app.helpers import send_email
from app.db_manager import sqliteManager as db

import sqlite3

import config


request_topic = Blueprint('request_topic', __name__)


@request_topic.route('/request_topic', methods=['POST'])
@at_least_role(UserRole.STUDENT)
def request_new_topic():
    if session['acc_type'] != 'student':
        # only students are allowed to request topics
        # disallow ALL other users from requesting
        return error('You must be a student to request a topic!')
    try:
        fields = ['topic', 'message']
        topic, message = get_fields(request.form, fields)
    except ValueError as e:
        return e.args
    db.connect()

    res = db.select_columns('topics', ['id', 'name', 'supervisor'],
                            ['id'], [topic])
    topic_name = res[0][1]
    supervisor = res[0][2]
    if not len(res):
        db.close()
        return error('No such topic exists!')

    res = db.select_columns('request_statuses', ['id'], ['name'], ['pending'])

    user_id = session['id']
    now = datetime.now().timestamp()
    try:
        db.insert_single('topic_requests',
                         [user_id, topic, res[0][0], now, message],
                         ['student', 'topic',
                          'status', 'date_created', 'text'])
    except sqlite3.IntegrityError:
        db.close()
        return error('You have already requested this topic!')

    res = db.select_columns('users', ['name', 'email'], ['id'], [supervisor])
    send_email(to=res[0][1], name=res[0][0], subject='New Topic Request',
               messages=[
                   'A student has requested a thesis topic on offer by you.',
                   f'The topic is titled "{topic_name}".',
                   'A message from the student is attached below:',
                   message.replace('\n', '<br>'),
                   'You can approve or reject the topic request ' +
                   f'<a href="{config.SITE_HOME}">here</a>.'
               ])

    db.close()
    return jsonify({'status': 'ok'})
