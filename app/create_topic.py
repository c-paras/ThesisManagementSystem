from flask import Blueprint
from flask import render_template
from flask import request
from flask import session

from app.auth import loggedin
from app.helpers import *

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
    print(details)
    return jsonify({'status': 'ok'})
