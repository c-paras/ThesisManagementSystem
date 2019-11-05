import json

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
from app.queries import queries
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
    hr_tag = '<hr style="border: 1px dashed;">'
    send_email(to=res[0][1], name=res[0][0], subject='New Topic Request',
               messages=[
                   'A student has requested a thesis topic on offer by you.',
                   f'The topic is titled "{topic_name}".',
                   f'A message from the student is attached below:{hr_tag}',
                   message.replace('\n', '<br>'),
                   f'{hr_tag}You can approve or reject the topic request ' +
                   f'<a href="{config.SITE_HOME}">here</a>.'
               ])

    db.close()
    return jsonify({'status': 'ok'})


@request_topic.route('/lookup_request', methods=['POST'])
@at_least_role(UserRole.STUDENT)
def lookup_request():
    data = json.loads(request.data)
    if session['acc_type'] == 'student' and\
       session['id'] != data['student_id']:
        return error('Lookup failure')

    db.connect()
    topic_req = queries.lookup_topic_request(data.get('student_id', -1),
                                             data.get('topic_id', -1))[0]
    db.close()

    # Convert to ms for javascript
    topic_req['reqDate'] = topic_req['reqDate'] * 1000
    return jsonify(topic_req)


@request_topic.route('/respond_request', methods=['POST'])
@at_least_role(UserRole.STAFF)
def respond_request():
    data = get_fields(request.form, ['response', 'student-id', 'topic'])
    db.connect()

    req_status = 'approved' if data[0] == 'accept' else 'rejected'
    if req_status == 'approved':
        if 'assessor' not in request.form:
            db.close()
            return error('You must specify an assessor')
        db.insert_single('student_topic',
                         [data[1], data[2], request.form['assessor']],
                         ['student', 'topic', 'assessor'])

    queries.respond_topic(data[1], data[2], req_status,
                          datetime.now().timestamp())
    res = db.select_columns('users', ['email', 'name'],
                            ['id'], [data[1]])[0]
    student = {
        'email': res[0],
        'name': res[1]
    }
    topic = db.select_columns('topics', ['name'], ['id'], [data[2]])[0][0]
    db.close()

    send_email(student['email'], student['name'], 'Topic Reply',
               [f'Your topic request for "{topic}" has been {req_status}.'])
    return jsonify({'status': 'ok'})
