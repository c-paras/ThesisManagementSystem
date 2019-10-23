from flask import Blueprint
from flask import render_template
from flask import request
from flask import session

from app.auth import UserRole
from app.auth import at_least_role
from app.helpers import *
from app.db_manager import sqliteManager as db


create_topic = Blueprint('create_topic', __name__)


@create_topic.route('/create_topic', methods=['GET', 'POST'])
@at_least_role(UserRole.STAFF)
def create():
    if request.method == 'GET':
        return render_template(
            'create_topic.html',
            heading='Create Topic',
            title='Create Topic')

    try:
        fields = ['topic', 'areas', 'details']
        topic, areas, details = get_fields(request.form, fields)
    except Exception as e:
        return e.args

    prereqs = list(dict.fromkeys(request.form.getlist('prerequisites')))
    prereqs = [x.lower() for x in prereqs]

    areas = areas.split(',')

    db.connect()
    user_id = session['id']
    res = db.select_columns('topics', ['name'], ['name'], [topic])

    # only check the name of the topic
    if len(res):
        db.close()
        return error('A topic with that name already exists!')

    db.insert_single(
        'topics',
        [topic, user_id, details],
        ['name', 'supervisor', 'description']
        )
    topic_id = db.select_columns('topics', ['id'], ['name'], [topic])[0][0]

    for area in areas:
        area = area.strip()
        db.insert_single('topic_areas', [topic_id, area],
                         ['topic', 'name'])

    # for prereq in prereqs:
    #
    #     prereq = prereq.strip()
    #     course_id = db.select_columns(
    #         'courses', ['id'], ['code'], [prereq]
    #         )
    #     db.insert_single(
    #         'prerequisites',
    #         [0, course_id, topic_id],
    #         ['type', 'course', 'topic']
    #         )

    db.close()
    return jsonify({'status': 'ok'})
