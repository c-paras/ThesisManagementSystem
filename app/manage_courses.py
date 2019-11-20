from datetime import datetime
from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from flask import session

from app.auth import at_least_role, UserRole
from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload
from app.helpers import error, get_fields, timestamp_to_string, zid_sort
from app.queries import queries
from app.update_accounts import update_from_file, update_account_type
from app.update_accounts import get_all_account_types

import json
import re

import config

manage_courses = Blueprint('manage_courses', __name__)


# allow for a defaults course or don't reset which course they are on
# and reformat the name so it looks better in list
@manage_courses.route('/manage_courses', methods=['GET', 'POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def manage_course_offerings():

    data = {}
    if request.method == 'POST':
        data = json.loads(request.data)
        if 'table' in data:
            if data['table'] == 'update_account_types':
                db.connect()
                if not re.match(config.EMAIL_FORMAT, data['email']):
                    db.close()
                    return error(f"""Invalid email address<br>
                        {config.EMAIL_FORMAT_ERROR}""")
                update_account_type(
                    data['email'], data['name'],
                    data['account_type'], session['current_co']
                )
                db.close()

            if data['table'] == 'materials':
                db.connect()
                db.update_rows(
                    'materials',
                    [data['type']], ['visible'],
                    ['id'], [data['id']]
                )
                db.close()

            if data['table'] == 'tasks':
                db.connect()
                db.update_rows(
                    'tasks',
                    [data['type']], ['visible'],
                    ['id'], [data['id']]
                )
                db.close()
        return jsonify({'status': 'ok'})

    co = 1
    if 'current_co' in session:
        co = session['current_co']
    else:
        session['current_co'] = co
        # maybe default to whatever course is in the current session
    db.connect()
    course_offerings = queries.get_course_offering_details()
    co_map, courses, sessions = split_co(course_offerings)
    materials_query = db.select_columns(
        'materials', ['id', 'name', 'visible'], ['course_offering'], [co]
    )
    materials = []
    for material in materials_query:
        attachments = []
        attachments_query = db.select_columns(
            'material_attachments', ['path'], ['material'], [material[0]]
        )
        for x in attachments_query:
            attachments.append(FileUpload(filename=x[0]))
        materials.append((material[0], material[1], attachments, material[2]))
    tasks = []
    task_query = db.select_columns(
        'tasks', ['id', 'name', 'deadline', 'visible'],
        ['course_offering'], [co]
    )
    task_ids = []
    task_query.sort(key=lambda x: x[2])
    for task in task_query:
        attachments = []
        attachments_query = db.select_columns(
            'task_attachments', ['path'], ['task'], [task[0]]
        )
        for x in attachments_query:
            attachments.append(FileUpload(filename=x[0]))

        print_date = timestamp_to_string(task[2])
        tasks.append((task[0], task[1], print_date, attachments, task[3]))
        task_ids.append(task[0])
    enrollments = []
    enrollments_query = queries.get_student_enrollments(co)
    for student in enrollments_query:
        zid = student[2].split('@')[0]
        if student[3] is not None:
            enrollments.append((student[1], zid, student[2], student[3],
                                student[0]))
        else:
            enrollments.append((student[1], zid, student[2], 'No topic',
                                student[0]))

    # for material file upload
    file_types = db.select_columns('file_types', ['name'])
    file_types = list(map(lambda x: x[0], file_types))
    allowed_file_types = ','.join(file_types)
    account_types = get_all_account_types()
    accepted_account_types = [
        ('student', account_types['student']),
        ('admin', account_types['course_admin'])
    ]
    sessions_list = sessions[co_map[co]['course']]
    enrollments.sort(key=lambda x: zid_sort(x[1]))
    db.close()
    return render_template(
        'manage_courses.html',
        title='Manage Courses',
        heading='Manage Courses',
        materials=materials,
        tasks=tasks,
        enrollments=enrollments,
        courses=courses,
        sessions=sessions_list,
        co_map=co_map,
        default_co=co,
        max_file_size=config.MAX_FILE_SIZE,
        accepted_files=allowed_file_types,
        task_ids=task_ids
    )


def split_co(course_offerings):
    co_map = {}
    courses = {}
    sessions = {}
    for co in course_offerings:
        if co[0] not in co_map:
            temp = {
                'course': co[4],
                'session': co[5],
            }
            co_map[co[0]] = temp

        if co[4] not in courses:
            courses[co[4]] = co[1]
            sessions[co[4]] = []

        if co[3] < 2019:
            print(co[3])
            ses_string = str(co[3])[2:] + 'S' + str(co[2])
        else:
            ses_string = str(co[3])[2:] + 'T' + str(co[2])
        sessions[co[4]].append((ses_string, co[5]))
    return co_map, courses, sessions


@manage_courses.route('/update_course_offering', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def update_course_offering():
    data = json.loads(request.data)
    db.connect()
    course_id = data[0]['value']
    session_id = data[1]['value']
    res = db.select_columns(
        'course_offerings', ['id'],
        ['session', 'course'],
        [session_id, course_id]
    )
    db.close()
    if len(res) > 0:
        session['current_co'] = res[0][0]
        return jsonify({'status': 'ok'})
    else:
        return error("Failed to find course offering")


@manage_courses.route('/get_sessions', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def get_sessions():
    data = json.loads(request.data)
    db.connect()
    res = db.select_columns(
        'course_offerings', ['session'], ['course'], [data]
    )
    sessions = []
    for co in res:
        ses_details = db.select_columns(
            'sessions', ['year', 'term'], ['id'], [co[0]]
        )[0]
        if ses_details[0] < 2019:
            print(ses_details[0])
            ses_string = str(ses_details[0])[2:] + 'S' + str(ses_details[1])
        else:
            ses_string = str(ses_details[0])[2:] + 'T' + str(ses_details[1])
        sessions.append((ses_string, co[0]))
    db.close()
    if len(session) > 0:
        return jsonify({
            'status': 'ok',
            'data': sessions
        })
    else:
        return error("Failed to find sessions")


@manage_courses.route('/enrol_user', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def upload_enroll_user():
    data = json.loads(request.data)
    if 'table' in data and data['table'] == 'update_account_types':
        db.connect()
        if not re.match(config.EMAIL_FORMAT, data['email']):
            db.close()
            return error(f"""Invalid email address<br>
                {config.EMAIL_FORMAT_ERROR}""")
        update_account_type(
            data['email'], data['name'],
            data['account_type'], session['current_co']
        )
        db.close()
    return jsonify({'status': 'ok'})


@manage_courses.route('/upload_enrollments', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def upload_enroll_file():
    try:
        enroll_file = FileUpload(req=request)
    except KeyError:
        return error('Could not find a file to upload')

    if enroll_file.get_extention() != '.csv':
        return error('File type must be csv')

    if enroll_file.get_size() > config.MAX_FILE_SIZE:
        return error('File is too large')
    enroll_file.commit()
    db.connect()
    error_string = update_from_file(
        enroll_file.get_path(), session['current_co'], 'student'
    )
    db.close()
    enroll_file.remove_file()
    if error_string != "":
        return error(error_string)
    return jsonify({'status': 'ok'})


@manage_courses.route('/upload_material', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def upload_material():
    try:
        fields = ['file-label', 'file-name', 'course-offering',
                  'old-material-id', 'delete-old-file']
        file_label, file_name, course_offering, old_material_id, \
            delete_old_file = \
            get_fields(request.form, fields,
                       optional=['word-limit', 'file-name'],
                       ints=['course-offering'])
    except ValueError as e:
        return e.args[0]
    db.connect()

    try:
        old_material_id = int(old_material_id)
    except ValueError as e:
        old_material_id = None

    # check if no file when there should be one
    if file_name == '' and \
            (delete_old_file == 'true' or old_material_id is None):
        return error('File Name is required!')

    # check if course offering is valid
    res = db.select_columns('course_offerings', ['id'],
                            ['id'], [course_offering])
    if not len(res):
        db.close()
        return error('Cannot attach material to unknown course offering')

    # check if material with same label exists in course
    res = db.select_columns('materials', ['id'],
                            ['name', 'course_offering'],
                            [file_label, course_offering])
    if len(res) and old_material_id != res[0][0]:
        db.close()
        return error('An item with that label already exists in this course')

    # otherwise, we can insert the material into the course
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

    if delete_old_file == 'true':
        old = db.select_columns('material_attachments', ['path'],
                                ['material'],
                                [old_material_id])
        if old:
            db.delete_rows('material_attachments', ['material'],
                           [old_material_id])
            try:
                prev_submission = FileUpload(filename=old[0][0])
                prev_submission.remove_file()
            except LookupError:
                # If the file doesn't exists don't worry as we are deleting
                # the attachment anyway
                pass

    if old_material_id is not None:
        # update existing material entries
        db.update_rows('materials',
                       [file_label], ['name'],
                       ['id'], [old_material_id])
        db.update_rows('materials',
                       [file_label], ['name'],
                       ['id'], [old_material_id])
        if delete_old_file == 'true':
            db.insert_single('material_attachments',
                             [old_material_id, sent_file.get_name()],
                             ['material', 'path'])
    else:
        # add material and file path to db
        db.insert_single('materials',
                         [course_offering, file_label, 0],
                         ['course_offering', 'name', 'visible'])
        res = db.select_columns('materials', ['id'],
                                ['name', 'course_offering'],
                                [file_label, course_offering])
        db.insert_single('material_attachments',
                         [res[0][0], sent_file.get_name()],
                         ['material', 'path'])
    db.close()
    return jsonify({'status': 'ok'})


@manage_courses.route('/create_course', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def create_course():
    db.connect()
    curr_year = datetime.now().year
    num_terms = queries.get_terms_per_year(curr_year)
    course = {
        'offerings': [False for _ in range(num_terms)]
    }
    try:
        res = get_fields(request.form,
                         ['title', 'code', 'description', 'year'],
                         ['year'])
        for i in range(num_terms):
            if str(i + 1) in request.form:
                course['offerings'][i] = True
    except ValueError as e:
        db.close()
        return e.args[0]

    course['title'] = res[0]
    course['code'] = res[1]
    course['description'] = res[2]

    if not re.match(config.COURSE_CODE_FORMAT, course['code']):
        db.close()
        return error("Invalid course code")

    course['year'] = int(res[3])
    if curr_year > course['year']:
        db.close()
        return error(f"Year must be at least {curr_year}")

    if True not in course['offerings']:
        db.close()
        return error('You must select at least one term offering')

    sessions = queries.get_course_sessions(course['code'])
    sessions = filter(lambda s: s[0] == course['year'], sessions)
    for year, term in sessions:
        if course['offerings'][term - 1]:
            db.close()
            return error(f"{course['code']} already offered in {year} T{term}")

    db.insert_single('courses',
                     [course['code'], course['title'], course['description']],
                     ['code', 'name', 'description'])
    res = db.select_columns('courses', ['id'], ['code'], [course['code']])
    course['id'] = res[0][0]

    query = []
    for i in range(len(course['offerings'])):
        if not course['offerings'][i]:
            continue
        res = db.select_columns('sessions', ['id'],
                                ['year', 'term'],
                                [course['year'], i + 1])
        session_id = res[0][0]
        query.append(('course_offerings',
                      [course['id'], session_id],
                      ['course', 'session']))
    db.insert_multiple(query)
    db.close()
    return jsonify({'status': 'ok'})


@manage_courses.route('/export_marks', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def exportMarks():
    db.connect()
    data = json.loads(request.data)
    studentIds = data['studentIds']
    taskIds = data['taskIds']
    details = {}
    ass_and_sup = []
    for ids in studentIds:
        student_query = db.select_columns('users', ['name', 'email', 'id'],
                                          ['id'], [ids])
        ass_and_sup_query = queries.get_user_ass_sup(ids)

        if ass_and_sup_query:
            ass_and_sup = (ass_and_sup_query[0][0], ass_and_sup_query[0][1])
        else:
            ass_and_sup = (None, None)

        for task in taskIds:
            task_query = db.select_columns('tasks', ['name', 'id'],
                                           ['id'], [task])
            ass_name = db.select_columns('users', ['name'], ['id'],
                                         [ass_and_sup[0]])
            super_name = db.select_columns('users', ['name'], ['id'],
                                           [ass_and_sup[1]])

            if not ass_name:
                ass_name = [('Not Assigned',)]

            if not super_name:
                super_name = [('Not Assigned',)]

            details[(student_query[0][2],
                     task_query[0][1])] = [student_query[0][0],
                                           student_query[0][1].split('@')[0],
                                           task_query[0][0], '-', '-',
                                           ass_and_sup[0], ass_and_sup[1],
                                           task_query[0][1], ass_name[0][0],
                                           super_name[0][0]]

    task_criteria = []
    for task in taskIds:
        task_criteria_query = db.select_columns('task_criteria',
                                                ['id', 'task'],
                                                ['task'], [task])
        for crit in task_criteria_query:
            task_criteria.append(crit)

    for crit in task_criteria:

        for student in studentIds:
            # assessor
            if (details[(student, crit[1])][5] is not None):
                marks_query = db.select_columns('marks', ['mark'],
                                                ['criteria', 'student',
                                                'marker'],
                                                [crit[0], student,
                                                details[(student,
                                                         crit[1])][5]])
                if marks_query:
                    if (details[(student, crit[1])][3] == '-'):
                        details[(student, crit[1])][3] = marks_query[0][0]
                    else:
                        details[(student, crit[1])][3] = details[(student,
                                                                  crit[1])][3]\
                                                         + marks_query[0][0]

            # supervisor
            if (details[(student, crit[1])][6] is not None):
                marks_query = db.select_columns('marks', ['mark'],
                                                ['criteria', 'student',
                                                'marker'],
                                                [crit[0], student,
                                                details[(student,
                                                         crit[1])][6]])
                if marks_query:
                    if (details[(student, crit[1])][4] == '-'):
                        details[(student, crit[1])][4] = marks_query[0][0]
                    else:
                        details[(student, crit[1])][4] = details[(student,
                                                                  crit[1])][4]\
                                                         + marks_query[0][0]
    db.close()

    return jsonify({'status': 'ok', 'details': list(details.values())})


@manage_courses.route('/delete_task', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def delete_task():
    data = json.loads(request.data)
    task_id = data['taskId']

    db.connect()
    submissions = db.select_columns('submissions', ['name'],
                                    ['task'], [task_id])

    if submissions:
        return jsonify({'status': 'fail',
                        'message': "Unable to delete - \
                         Students have already made submissions"})

    db.delete_rows('tasks', ['id'], [task_id])
    db.delete_rows('task_attachments', ['task'], [task_id])
    db.delete_rows('task_criteria', ['task'], [task_id])

    db.close()
    return jsonify({'status': 'ok', "message": "Deleted Task"})


@manage_courses.route('/check_delete_task', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def check_delete_task():
    data = json.loads(request.data)
    task_id = data['taskId']

    db.connect()
    submissions = db.select_columns('submissions', ['name'],
                                    ['task'], [task_id])

    if submissions:
        return jsonify({'status': 'fail',
                        'message': "Unable to delete - \
                         Students have already made submissions"})

    db.close()
    return jsonify({'status': 'ok', "message": "Deleted Task"})


@manage_courses.route('/delete_material', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def delete_material():
    data = json.loads(request.data)
    material_id = data['materialId']

    db.connect()
    db.delete_rows('materials', ['id'], [material_id])
    db.delete_rows('material_attachments', ['material'], [material_id])

    return jsonify({'status': 'ok', "message": "Deleted Material"})
