from datetime import datetime

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from app.auth import at_least_role
from app.auth import UserRole
from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload
from app.helpers import error
from app.helpers import get_fields
from app.queries import queries

import config


create_task = Blueprint('create_task', __name__)


@create_task.route('/create_task', methods=['GET', 'POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def create():
    course_id = request.args.get('course_offering_id', None, type=int)
    if request.method == 'GET':
        if course_id is None:
            abort(400)
        db.connect()
        res = db.select_columns('course_offerings',
                                ['id'], ['id'], [course_id])
        if not len(res):
            db.close()
            abort(404)
        file_types = db.select_columns('file_types', ['name'])
        file_types = list(map(lambda x: x[0], file_types))
        allowed_file_types = ','.join(file_types)

        heading = 'Create Task'
        default_fields = {'task-name': '', 'deadline': '',
                          'task-description': '', 'submission-type': 'text',
                          'word-limit': '', 'maximum-file-size': '',
                          'accepted-file-type': '', 'marking-method': 'accept',
                          'criteria': []}

        # if updating old task then load old task data
        old_task_id = request.args.get('update', None, type=int)
        if old_task_id is not None:
            res = queries.get_past_task_data(old_task_id)
            if res is not None:
                res = res[0]
                heading = 'Edit Task'

                # basic task details
                default_fields['task-name'] = res[0]
                time_format = '%d/%m/%Y %H:%M'
                due_date = datetime.fromtimestamp(res[1])
                default_fields['deadline'] = due_date.strftime(time_format)
                default_fields['task-description'] = res[2]

                # submission method specific
                if res[3] == 'text submission':
                    default_fields['word-limit'] = res[4]
                else:
                    default_fields['submission-type'] = 'file'
                    default_fields['maximum-file-size'] = int(res[5])
                    default_fields['accepted-file-type'] = res[6]

                # marking method specifics
                if res[7] == 'requires mark':
                    default_fields['marking-method'] = 'criteria'

        db.close()
        return render_template('create_task.html', heading=heading,
                               title=heading, file_types=file_types,
                               course_id=course_id,
                               max_file_size=config.MAX_FILE_SIZE,
                               max_word_limit=config.MAX_WORD_LIMIT,
                               accepted_file_types=allowed_file_types,
                               old_task_id=old_task_id,
                               default_fields=default_fields)

    try:
        fields = [
            'task-name', 'deadline', 'task-description', 'submission-type',
            'word-limit', 'maximum-file-size', 'accepted-file-type',
            'marking-method', 'num-criteria', 'course-id', 'file-name'
        ]
        task_name, deadline, task_description, submission_type, \
            word_limit, max_file_size, accepted_ftype, marking_method, \
            num_criteria, course_id, file_name = \
            get_fields(request.form, fields,
                       optional=['word-limit', 'file-name'],
                       ints=['maximum-file-size', 'num-criteria',
                             'word-limit', 'course-id'])
    except ValueError as e:
        return e.args

    try:
        deadline = datetime.strptime(deadline, '%d/%m/%Y %H:%M').timestamp()
    except ValueError:
        return error('Invalid date format for deadline!')

    if submission_type == 'file':
        max_size = config.MAX_FILE_SIZE
        if not (1 <= max_file_size <= max_size):
            return error(
                f'Maximum file size must be between 1 and {max_size}!'
            )
    elif submission_type == 'text':
        try:
            word_limit = get_fields(request.form,
                                    ['word-limit'], ints=['word-limit'])[0]
        except ValueError as e:
            return e.args
        max_word_limit = config.MAX_WORD_LIMIT
        if not (1 <= word_limit <= max_word_limit):
            return error(
                f'Word limit must be between 1 and {max_word_limit}!'
            )
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
    res = db.select_columns('course_offerings', ['id'], ['id'], [course_id])
    if not len(res):
        db.close()
        return error('Cannot create task for unknown course!')
    res = db.select_columns('tasks', ['name'], ['name', 'course_offering'],
                            [task_name, course_id])
    if len(res):
        db.close()
        return error('A task with that name already exists in this course!')

    # retrieve some foreign keys for insertion
    res = db.select_columns('file_types', ['id'], ['name'], [accepted_ftype])
    if not len(res):
        db.close()
        return error('Invalid or unsupported file type!')
    file_type_id = res[0][0]

    # upload file if present
    sent_file = None
    if len(file_name):
        try:
            sent_file = FileUpload(req=request)
        except KeyError:
            db.close()
            return error('Could not find a file to upload')

        res = db.select_columns('file_types', ['name'])
        file_types = list(map(lambda x: x[0], res))
        if sent_file.get_extention() not in file_types:
            db.close()
            accept_files = ', '.join(file_types)
            return error(f'Accepted file types are: {accept_files}')
        if sent_file.get_size() > config.MAX_FILE_SIZE:
            sent_file.remove_file()
            db.close()
            return error(
                f'File exceeds the maximum size of {config.MAX_FILE_SIZE} MB'
            )
        sent_file.commit()

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
        [task_name, course_id, deadline, task_description,
         max_file_size, 0, submission_method_id, mark_method_id, word_limit],
        ['name', 'course_offering', 'deadline', 'description', 'size_limit',
         'visible', 'submission_method', 'marking_method', 'word_limit']
    )

    res = db.select_columns('tasks', ['id'],
                            ['name', 'course_offering'],
                            [task_name, course_id])
    task_id = res[0][0]

    if sent_file:
        db.insert_single('task_attachments',
                         [task_id, sent_file.get_name()],
                         ['task', 'path'])

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
