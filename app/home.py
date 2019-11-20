from flask import Blueprint
from flask import render_template
from flask import session
from flask import request
from flask import jsonify

from datetime import datetime

from app.auth import at_least_role
from app.auth import UserRole
from app.file_upload import FileUpload
from app.db_manager import sqliteManager as db
from app.queries import queries
from app.helpers import error
from app.helpers import zid_sort
from app.update_accounts import update_from_file, update_account_type
from app.update_accounts import get_all_account_types

import json
import re
import config

home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
@home.route('/home', methods=['GET'])
@home.route('/dashboard', methods=['GET'])
@at_least_role(UserRole.PUBLIC)
def dashboard():
    user_type = session['acc_type']

    if user_type == 'student':
        return student_dashboard()
    elif user_type == 'public':
        return render_template('home_public.html',
                               heading='My Dashboard',
                               title='My Dashboard')
    else:
        return staff_dashboard()


def student_dashboard():
    db.connect()
    all_materials = queries.get_user_materials(session['id'])

    cur_materials = []
    for material in all_materials:
        # now = datetime.now().timestamp()
        # if now < material[2] or now > material[3]:
        # if we wanted to split current, previous or
        # future we would do the above line
        attachments = []
        attachments_query = db.select_columns(
            'material_attachments', ['path'], ['material'], [material[0]]
        )
        for x in attachments_query:
            attachments.append(FileUpload(filename=x[0]))
        cur_materials.append((material[1], attachments, material[4]))

    assessor = -1
    supervisor = -1
    markers = queries.get_user_ass_sup(session['id'])
    if len(markers) > 0:
        assessor = markers[0][0]
        supervisor = markers[0][1]

    tasks = []
    my_tasks = queries.get_user_tasks(session['id'])
    for task in my_tasks:
        status = get_sub_status(session['id'], task[0])
        if 'approval' in task[3]:
            tasks.append((
                task[2], task[1], status, '-', '-',
                task[0], task[4]
            ))
        else:
            criteria = db.select_columns(
                'task_criteria', ['id', 'max_mark'], ['task'], [task[0]]
            )
            total_max_mark = 0
            supervisor_mark = 0
            assessor_mark = 0
            for c in criteria:
                total_max_mark += c[1]
                if assessor is not None and assessor != -1:
                    mark = db.select_columns(
                        'marks', ['mark'],
                        ['criteria', 'student', 'marker'],
                        [c[0], session['id'], assessor]
                    )
                    if len(mark) != 0:
                        assessor_mark += mark[0][0]
                    else:
                        assessor_mark = -1
                if supervisor is not None and supervisor != -1:
                    mark = db.select_columns(
                        'marks', ['mark'],
                        ['criteria', 'student', 'marker'],
                        [c[0], session['id'], supervisor]
                    )
                    if len(mark) != 0:
                        supervisor_mark += mark[0][0]
                    else:
                        supervisor_mark = -1
            if supervisor_mark <= 0:
                supervisor_mark = '-'
            if assessor_mark <= 0:
                assessor_mark = '-'
            tasks.append((
                task[2], task[1], status, supervisor_mark, assessor_mark,
                task[0], task[4]
            ))

    # get info about selected topic and assigned supervisor/assessor
    try:
        sup = db.select_columns('users', ['name', 'email'],
                                ['id'], [supervisor])[0]
        has_sup = True
    except IndexError:
        sup = 'Not assigned'  # should not happen anyway
        has_sup = False
    try:
        assess = db.select_columns('users', ['name', 'email'],
                                   ['id'], [assessor])[0]
        has_assess = True
    except IndexError:
        assess = 'Not assigned'
        has_assess = False
    try:
        topic = queries.get_student_topic(session['id'])[0][0]
        has_topic = True
    except IndexError:
        topic = 'You have not selected a topic yet.'
        has_topic = False
    topic_info = {
        'has_topic': has_topic,
        'topic': topic,
        'supervisor': sup,
        'assessor': assess,
        'has_supervisor': has_sup,
        'has_assessor': has_assess
    }

    tasks.sort(key=lambda x: (x[0], x[6]))
    db.close()
    return render_template('home_student.html',
                           heading='My Dashboard',
                           title='My Dashboard',
                           materials=cur_materials,
                           tasks=tasks,
                           topic_info=topic_info)


def get_sub_status(user, task):
    status = 'not submitted'
    submission = db.select_columns(
        'submissions',
        ['status'],
        ['student', 'task'],
        [user, task]
    )
    if len(submission) > 0:
        status_name = db.select_columns(
            'request_statuses',
            ['name'],
            ['id'],
            [submission[0][0]]
        )
        status = status_name[0][0]
    return status


def staff_dashboard():
    db.connect()
    curr_requests = [{'stu_id': r[0],
                      'topic_id': r[1],
                      'stu_name': r[2],
                      'stu_email': r[3],
                      'topic_name': r[4],
                      'date_created': r[5]}
                     for r in queries.get_curr_topic_requests(session['user'])]

    curr_requests = sorted(curr_requests, key=lambda i:
                           i['date_created'], reverse=True)

    # the way of deciding between current and past students
    # is by testing start/end date and current unix timestamp
    curr_students = []
    past_students = []

    # get students who I am supervising
    super_students = queries.get_current_super_students(session['user'])

    # get students who I am assessing
    assess_students = queries.get_current_assess_students(session['user'])

    # now group up the students & role types
    for tup_student in super_students:
        i = list(tup_student)
        i.append('Supervisor')
        if datetime.now().timestamp() < i.pop(4):
            curr_students.append(i)
        else:
            past_students.append(i)

    for tup_student in assess_students:
        i = list(tup_student)
        i.append('Assessor')
        if datetime.now().timestamp() < i.pop(4):
            curr_students.append(i)
        else:
            past_students.append(i)

    curr_students.sort(key=lambda x: zid_sort(x[1]))
    past_students.sort(key=lambda x: zid_sort(x[1]))
    # for the approve/reject topic dropdown
    potential_assessors = filter(lambda s: s['id'] != session['id'],
                                 queries.get_users_of_type('supervisor') +
                                 queries.get_users_of_type('course_admin'))

    db.close()
    return render_template('home_staff.html',
                           heading='My Dashboard',
                           title='My Dashboard',
                           curr_requests=curr_requests,
                           curr_students=curr_students,
                           past_students=past_students,
                           assessors=potential_assessors)


@home.route('/add_staff', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def add_staff():
    data = json.loads(request.data)
    if 'table' in data and data['table'] == 'update_account_types':
        db.connect()
        if not re.match(config.EMAIL_FORMAT, data['email']):
            db.close()
            return error(f"""Invalid email address<br>
                {config.EMAIL_FORMAT_ERROR}""")
        update_account_type(
            data['email'], data['name'],
            data['account_type']
        )
        db.close()
    return jsonify({'status': 'ok'})


@home.route('/upload_staff', methods=['POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def upload_staff():
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
        enroll_file.get_path(), default='supervisor'
    )
    db.close()
    enroll_file.remove_file()
    if error_string != "":
        return error(error_string)
    return jsonify({'status': 'ok'})
