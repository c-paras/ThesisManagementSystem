from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import jsonify
from flask import request

from app.auth import UserRole
from app.auth import at_least_role
from app.helpers import error

create_task = Blueprint('create_task', __name__)


@create_task.route('/create_task', methods=['GET', 'POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def create():
    if request.method == 'GET':
        return render_template('create_task.html', heading='Create Task',
                               title='Create Task')

    # TODO: post request
    return error('A task with that name already exists!')
    return jsonify({'status': 'ok'})
