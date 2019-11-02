from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import jsonify
from flask import request

from app.auth import UserRole
from app.auth import at_least_role
from app.helpers import error
from app.helpers import get_fields
from app.db_manager import sqliteManager as db

create_task = Blueprint('create_task', __name__)


@create_task.route('/create_task', methods=['GET', 'POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def create():
    db.connect()
    if request.method == 'GET':
        file_types = db.select_columns('file_types', ['name'])
        file_types = list(map(lambda x: x[0], file_types))
        db.close()
        return render_template('create_task.html', heading='Create Task',
                               title='Create Task', file_types=file_types)

    try:
        fields = [
            'task-name', 'due-date', 'task-description', 'submission-type',
            'word-limit', 'maximum-file-size', 'accepted-file-type',
            'marking-method', 'criteria-1', 'max-mark-1'
        ]
        fields = get_fields(request.form, fields, ['word-limit'])
    except ValueError as e:
        return e.args

    print(fields)

    db.close()
    return error('A task with that name already exists!')

    db.close()
    return jsonify({'status': 'ok'})
