from flask import Blueprint
from flask import render_template
from flask import session

from datetime import datetime

from app.auth import UserRole
from app.auth import at_least_role
from app.queries import queries
from app.db_manager import sqliteManager as db


home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
@home.route('/home', methods=['GET'])
@home.route('/dashboard', methods=['GET'])
@at_least_role(UserRole.PUBLIC)
def dashboard():
    user_type = session['acc_type']
    is_student = user_type in ['public', 'student']
    # TODO: public user home page
    if is_student:
        return student_dashboard()
    else:
        return staff_dashboard()


def student_dashboard():
    db.connect()
    all_materials = queries.get_user_materials(session['id'])

    cur_materials = []
    for material in all_materials:
        now = datetime.now().timestamp()
        # if now < material[2] or now > material[3]:
        # if we wanted to split current, previous or
        # future we would do the above line
        attachments = db.select_columns(
            'material_attachments',
            ['path'],
            ['id'],
            [material[0]]
        )
        cur_attachments = []
        for attachment in attachments:
            cur_attachments.append(attachment[0])
        cur_materials.append((material[1], cur_attachments))

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
                task[2], task[1], status, '-', '-'
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
                task[2], task[1], status, supervisor_mark, assessor_mark
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
    curr_requests = queries.get_curr_topic_requests(session['user'])

    # need to implement way of deciding between current and past students, best
    # way would probably be by testing start/end date and current unix
    # timestamp. Need to wait until 'user_session' table is filled before
    # this is possible.

    curr_students = []
    past_students = []

    # get students who I am supervising
    super_students = queries.get_current_super_students(session['user'])

    # get students who I am assessing
    assess_students = queries.get_current_assess_students(session['user'])

    db.close()
    for tup_student in super_students:
        i = list(tup_student)
        i.append('Supervisor')
        if(datetime.now().timestamp() < i.pop(3)):
            curr_students.append(i)
        else:
            past_students.append(i)

    for tup_student in assess_students:
        i = list(tup_student)
        i.append('Assessor')
        if(datetime.now().timestamp() < i.pop(3)):
            curr_students.append(i)
        else:
            past_students.append(i)

    return render_template('home_staff.html',
                           heading='My Dashboard',
                           title='My Dashboard',
                           curr_requests=curr_requests,
                           curr_students=curr_students,
                           past_students=past_students)
