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

import json

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
        if 'table' in data and data['table'] == 'materials':
            db.connect()
            db.update_rows(
                'materials',
                [data['type']], ['visible'],
                ['id'], [data['id']]
            )
            db.close()

        if 'table' in data and data['table'] == 'tasks':
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
        pass  # maybe default to whatever course is in the current session
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
        date = datetime.fromtimestamp(task[2])
        print_date = date.strftime("%b %d %Y at %H:%M")
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
        accepted_files=allowed_file_types)


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
