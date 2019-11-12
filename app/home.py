from flask import Blueprint
from flask import render_template
from flask import session

from datetime import datetime

from app.auth import at_least_role
from app.auth import UserRole
from app.file_upload import FileUpload
from app.db_manager import sqliteManager as db
from app.queries import queries


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
        cur_materials.append((material[1], attachments))

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
                task[0]
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
                task[0]
            ))

    db.close()
    return render_template('home_student.html',
                           heading='My Dashboard',
                           title='My Dashboard',
                           materials=cur_materials,
                           tasks=tasks)


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
                      'topic_name': r[4]}
                     for r in queries.get_curr_topic_requests(session['user'])]

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
