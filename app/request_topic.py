from flask import Blueprint
from flask import request
from flask import session

from datetime import datetime

from app.auth import UserRole
from app.auth import at_least_role
from app.helpers import *
from app.db_manager import sqliteManager as db

import sqlite3


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

    res = db.select_columns('topics', ['id'], ['id'], [topic])
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

    db.close()
    return jsonify({'status': 'ok'})
