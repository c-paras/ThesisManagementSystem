from flask import Blueprint
from flask import render_template
from flask import request
from flask import session

from app.auth import loggedin
from app.helpers import *
from app.db_manager import sqliteManager as db
create_topic = Blueprint('create_topic', __name__)


@create_topic.route('/create_topic', methods=['GET', 'POST'])
@loggedin
def create():
    if request.method == 'GET':
        return render_template(
            'create_topic.html',
            heading='Thesis Management System - Create Topic',
            title='Create_topic')

    try:
        fields = ['topic', 'areas', 'details']
        topic, areas, details = get_fields(request.form, fields)
    except Exception as e:
        return e.args

    areas = areas.split(',')

    db.connect()
    user_id = session['id']
    res = db.select_columns('topics', ['name'], ['name'], [topic])

    # only check the name of the topic
    if len(res):
        db.close()
        return error('Topic has already exist')

    db.insert_single(
        'topics',
        [topic, user_id, details],
        ['name', 'supervisor', 'description']
    )
    topic_id = db.select_columns('topics', ['id'], ['name'], [topic])[0][0]
    print(topic_id)
    for area in areas:
        area = area.strip()
        db.insert_single('topic_areas',
                         [topic_id, area],
                         ['topic', 'name']
                         )

    db.close()
    return jsonify({'status': 'ok'})
