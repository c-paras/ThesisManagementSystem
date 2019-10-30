import json

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from flask import session

from app.auth import UserRole
from app.auth import at_least_role
from app.db_manager import sqliteManager as db
from app.queries import queries

manage_topic = Blueprint('manage_topic', __name__)


@manage_topic.route('/manage_topic', methods=['GET', 'POST'])
@at_least_role(UserRole.STAFF)
def manage():
    if request.method == 'GET':
        db.connect()
        curr_topics = queries.get_staff_curr_topics(session['user'])

        curr_topics = clean_topic_tuples(curr_topics)
        db.close()
        return render_template('manage_topic.html',
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
    for topic in curr_topics:
        # if it's in the dict, append values only
        if topic[0] in topic_dict:

            topic_dict[topic[0]] = topic_dict[topic[0]] + ', ' + topic[1]
        #  if it's not in the dict, create the entry
        else:

            topic_dict[topic[0]] = topic[1]
            visible.append(topic[2])

    return list(zip(list(topic_dict.keys()),
                    list(topic_dict.values()),
                    visible))
