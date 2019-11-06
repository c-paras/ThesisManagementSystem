from datetime import datetime

from flask import abort
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
    CO_id = request.args.get('course_offering_id', None, type=int)
    if request.method == 'GET':
        if CO_id is None:
            abort(400)
        db.connect()
        res = db.select_columns('course_offerings',
                                ['id'], ['id'], [CO_id])
        if not len(res):
            db.close()
            abort(404)
        file_types = db.select_columns('file_types', ['name'])
        file_types = list(map(lambda x: x[0], file_types))
        db.close()
        return render_template('create_task.html', heading='Create Task',
                               title='Create Task', file_types=file_types,
                               course_id=CO_id)

    try:
        fields = [
            'task-name', 'deadline', 'task-description', 'submission-type',
            'word-limit', 'maximum-file-size', 'accepted-file-type',
            'marking-method', 'num-criteria', 'course-id'
        ]
        task_name, deadline, task_description, submission_type, \
            word_limit, max_file_size, accepted_ftype, marking_method, \
            num_criteria, CO_id = \
            get_fields(request.form, fields, optional=['word-limit'],
                       ints=['maximum-file-size', 'num-criteria',
                             'word-limit', 'course-id'])
    except ValueError as e:
        return e.args

    try:
        deadline = datetime.strptime(deadline, '%Y/%m/%d %H:%M').timestamp()
    except ValueError:
        return error('Invalid date format for deadline!')

    if submission_type == 'file':
        if not (1 <= max_file_size <= 100):
            return error('Maximum file size must be between 1 and 100!')
    elif submission_type == 'text':
        try:
            word_limit = get_fields(request.form,
                                    ['word-limit'], ints=['word-limit'])[0]
        except ValueError as e:
            return e.args
        if not (1 <= word_limit <= 5000):
            return error('Word limit must be between 1 and 5000!')
    else:
        return error('Unknown submission type!')

    if marking_method == 'criteria':
        if num_criteria < 1:
            return error('At least one marking criterion is required!')
        else:
            criteria = [f'criteria-{i}' for i in range(1, num_criteria + 1)]
            marks = [f'maximum-mark-{i}' for i in range(1, num_criteria + 1)]
            try:
                criteria = get_fields(request.form, criteria)
                marks = get_fields(request.form, marks, ints=marks)
            except ValueError as e:
                return e.args

        if sum([mark for mark in marks]) != 100:
            return error('Marks must add to 100!')
    elif marking_method != 'accept':
        return error('Unknown marking method!')

    db.connect()
    res = db.select_columns('course_offerings', ['id'], ['id'], [CO_id])
    if not len(res):
        db.close()
        return error('Cannot create task for unknown course!')
    res = db.select_columns('tasks', ['name'], ['name', 'course_offering'],
                            [task_name, CO_id])
    if len(res):
        db.close()
        return error('A task with that name already exists in this course!')

    # retrieve some foreign keys for insertion
    res = db.select_columns('file_types', ['id'], ['name'], [accepted_ftype])
    if not len(res):
        db.close()
        return error('Invalid or unsupported file type!')
    file_type_id = res[0][0]
    res = db.select_columns('submission_methods', ['id'],
                            ['name'],
                            ['{} submission'.format(submission_type)])
    submission_method_id = res[0][0]
    marking_method = 'approval' if marking_method == 'accept' else 'mark'
    res = db.select_columns('marking_methods', ['id'], ['name'],
                            ['requires {}'.format(marking_method)])
    mark_method_id = res[0][0]

    # commit task
    db.insert_single(
        'tasks',
        [task_name, CO_id, deadline, task_description,
         max_file_size, 0, submission_method_id, mark_method_id, word_limit],
        ['name', 'course_offering', 'deadline', 'description', 'size_limit',
         'visible', 'submission_method', 'marking_method', 'word_limit']
    )

    res = db.select_columns('tasks', ['id'],
                            ['name', 'course_offering'],
                            [task_name, CO_id])
    task_id = res[0][0]

    # commit accepted file type
    db.insert_single('submission_types', [file_type_id, task_id],
                     ['file_type', 'task'])

    # commit marking criteria
    marking_criteria = []
    if marking_method == 'approval':
        marking_criteria.append(('task_criteria',
                                [task_id, 'Approval', 100],
                                ['task', 'name', 'max_mark']))
    else:
        for i in range(len(criteria)):
            marking_criteria.append(('task_criteria',
                                    [task_id, criteria[i], marks[i]],
                                    ['task', 'name', 'max_mark']))
    db.insert_multiple(marking_criteria)

    db.close()
    return jsonify({'status': 'ok'})
