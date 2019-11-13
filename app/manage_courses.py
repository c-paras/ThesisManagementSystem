from datetime import datetime
from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from flask import session

from app.auth import at_least_role
from app.auth import UserRole
from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload
from app.helpers import error
from app.helpers import get_fields
from app.queries import queries
from app.helpers import timestamp_to_string
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
                    return error("Invalid email address")
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

        if 'name' in data and data['name'] == 'courses':
            session['current_co'] = data['value']
        return jsonify({'status': 'ok'})

    co = 1
    if 'current_co' in session:
        co = session['current_co']
    else:
        session['current_co'] = co
        # maybe default to whatever course is in the current session
    db.connect()
    courses = queries.get_course_offering_details()
    courses.reverse()
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
    for task in task_query:
        attachments = []
        attachments_query = db.select_columns(
            'task_attachments', ['path'], ['task'], [task[0]]
        )
        for x in attachments_query:
            attachments.append(FileUpload(filename=x[0]))

        print_date = timestamp_to_string(task[2])
        tasks.append((task[0], task[1], print_date, attachments, task[3]))
    enrollments = []
    enrollments_query = queries.get_student_enrollments(co)
    for student in enrollments_query:
        zid = student[2].split('@')[0]
        if student[3] is not None:
            enrollments.append((student[1], zid, student[2], student[3]))
        else:
            enrollments.append((student[1], zid, student[2], 'No topic'))

    # for material file upload
    file_types = db.select_columns('file_types', ['name'])
    file_types = list(map(lambda x: x[0], file_types))
    allowed_file_types = ','.join(file_types)
    account_types = get_all_account_types()
    accepted_account_types = [
        ('student', account_types['student']),
        ('admin', account_types['course_admin'])
    ]
    db.close()
    return render_template(
        'manage_courses.html',
        title='Manage Courses',
        heading='Manage Courses',
        materials=materials,
        tasks=tasks,
        enrollments=enrollments,
        courses=courses,
        default_co=co,
        max_file_size=config.MAX_FILE_SIZE,
        accepted_files=allowed_file_types,
        account_types=accepted_account_types
    )


@manage_courses.route('/upload_enrollments', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def upload_enroll():
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
        enroll_file.get_path(), session['current_co']
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
        fields = ['file-label', 'file-name', 'course-offering']
        file_label, file_name, course_offering = get_fields(
            request.form, fields, ints=['course-offering'])
    except ValueError as e:
        return e.args[0]
    db.connect()

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
    if len(res):
        db.close()
        return error('An item with that label already exists in this course')

    # otherwise, we can insert the material into the course
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
