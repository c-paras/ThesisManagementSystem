from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import jsonify
from flask import request

from app.auth import UserRole
from app.auth import at_least_role
from app.helpers import error
from app.db_manager import sqliteManager as db

create_task = Blueprint('create_task', __name__)


@create_task.route('/create_task', methods=['GET', 'POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def create():
    if request.method == 'GET':
        db.connect()
        file_types = db.select_columns('file_types', ['name'])
        file_types = list(map(lambda x: x[0], file_types))
        db.close()
        return render_template('create_task.html', heading='Create Task',
                               title='Create Task', file_types=file_types)

    # TODO: post request
    return error('A task with that name already exists!')
    return jsonify({'status': 'ok'})
