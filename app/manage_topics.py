from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from flask import session

from app.auth import at_least_role
from app.auth import UserRole
from app.helpers import error
from app.db_manager import sqliteManager as db
from app.queries import queries

import json


manage_topics = Blueprint('manage_topics', __name__)


@manage_topics.route('/manage_topics', methods=['GET', 'POST'])
@at_least_role(UserRole.STAFF)
def manage():
    if request.method == 'GET':
        db.connect()
        curr_topics = queries.get_staff_curr_topics(session['user'])
        curr_topics = clean_topic_tuples(curr_topics)
        db.close()
        return render_template('manage_topics.html',
                               heading='Manage Topics',
                               title='Manage Topics',
                               curr_topics=curr_topics)

    data = json.loads(request.data)
    topic = []
    visible = []
    for x in data:
        topic.append(x)
        visible.append(data[x])

    db.connect()
    for i in range(len(topic)):
        db.update_rows('topics',
                       [visible[i]],
                       ['visible'],
                       ['name'],
                       [topic[i]])

    db.close()
    return jsonify({'status': 'ok'})


def clean_topic_tuples(curr_topics):
    topic_dict = dict()
    visible = []
    topic_id = []

    for topic in curr_topics:

        # if it's in the dict, append values only
        if topic[0] in topic_dict:
            topic_dict[topic[0]] = topic_dict[topic[0]] + ', ' + topic[1]

        # if it's not in the dict, create the entry
        else:
            topic_dict[topic[0]] = topic[1]
            visible.append(topic[2])
            topic_id.append(topic[3])

    return list(zip(list(topic_dict.keys()),
                    list(topic_dict.values()),
                    visible, topic_id))


@manage_topics.route('/delete_topic', methods=['POST'])
@at_least_role(UserRole.STAFF)
def delete_topic():
    data = json.loads(request.data)
    topic_id = data['topicId']
    db.connect()
    db.delete_rows('topics', ['id'], [topic_id])
    db.delete_rows('topic_to_area', ['topic'], [topic_id])
    db.delete_rows('announcements', ['topic'], [topic_id])
    db.delete_rows('prerequisites', ['topic'], [topic_id])
    db.close()
    return jsonify({'status': 'ok', "message": "Topic deleted"})


@manage_topics.route('/check_delete_topic', methods=['POST'])
@at_least_role(UserRole.STAFF)
def check_delete_topic():
    data = json.loads(request.data)
    topic_id = data['topicId']
    db.connect()
    # checking if a student has been enrolled in topic
    student_topic = db.select_columns('student_topic', ['student'],
                                      ['topic'], [topic_id])
    if student_topic:
        return error(
            'Cannot delete this topic!<br>There are enrolled students')

    # checking if a there is any pending topic requests
    pending = 'pending'
    pending_id = db.select_columns('request_statuses', ['id'],
                                   ['name'], [pending])
    topic_request = db.select_columns('topic_requests',
                                      ['student'], ['topic', 'status'],
                                      [topic_id, pending_id[0][0]])

    if topic_request:
        return error(
            'Cannot delete this topic!<br>There are pending topic requests.')
    db.close()
    return jsonify({'status': 'ok', "message": "Topic deleted"})
