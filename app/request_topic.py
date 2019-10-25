from flask import Blueprint
from flask import request
from flask import session

from datetime import datetime

from app.auth import UserRole
from app.auth import at_least_role
from app.helpers import *
from app.db_manager import sqliteManager as db


request_topic = Blueprint('request_topic', __name__)


@request_topic.route('/request_topic', methods=['POST'])
@at_least_role(UserRole.STUDENT)
def request_new_topic():
    try:
        fields = ['topic', 'message']
        topic, message = get_fields(request.form, fields)
    except ValueError as e:
        return e.args

    # TODO: handle possible error case where topic id is invalid
    # TODO: handle possible error case where topic already requested

    db.connect()
    user_id = session['id']
    now = datetime.now().timestamp()
    db.insert_single('topic_requests', [user_id, topic, 1, now, message],
                     ['student', 'topic', 'status', 'date_created', 'text'])

    db.close()
    return jsonify({'status': 'ok'})
