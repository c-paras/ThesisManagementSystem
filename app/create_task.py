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
    if request.method == 'GET':
        db.connect()
        file_types = db.select_columns('file_types', ['name'])
        file_types = list(map(lambda x: x[0], file_types))
        db.close()
        return render_template('create_task.html', heading='Create Task',
                               title='Create Task', file_types=file_types)

    try:
        fields = [
            'task-name', 'due-date', 'task-description', 'submission-type',
            'word-limit', 'maximum-file-size', 'accepted-file-type',
            'marking-method', 'num-criteria'
        ]
        task_name, due_date, description, submission_type, word_limit, \
            max_file_size, accecpted_ftype, marking_method, num_criteria = \
            get_fields(request.form, fields, optional=['word-limit'],
                       ints=['maximum-file-size', 'num-criteria'])
    except ValueError as e:
        return e.args
    num_criteria = num_criteria

    if marking_method == 'criteria':
        if num_criteria < 1:
            return error('At least one marking criterion is required!')
        else:
            criteria = [f'criteria-{i}' for i in range(1, num_criteria + 1)]
            marks = [f'maximum-mark-{i}' for i in range(1, num_criteria + 1)]
            try:
                criteria = get_fields(request.form, criteria)
                marks = get_fields(request.form, marks)
            except ValueError as e:
                return e.args

        if sum([mark for mark in marks]) != 100:
            return error('Marks must add to 100!')

    if submission_type == 'file':
        if not (1 <= max_file_size <= 100):
            return error('Maximum file size must be between 1 and 100!')

    db.connect()
    db.close()
    return error('A task with that name already exists in this course!')

    db.close()
    return jsonify({'status': 'ok'})
