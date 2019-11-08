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
from app.queries import queries

import json


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
    db.close()
    return render_template(
        'manage_courses.html',
        title='Manage Courses',
        heading='Manage Courses',
        materials=materials,
        tasks=tasks,
        enrollments=enrollments,
        courses=courses,
        default_co=co)
