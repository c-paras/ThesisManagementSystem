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
    my_id = session['id']
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
    db.close()
    return render_template('home_student.html',
                           heading='My Dashboard',
                           title='My Dashboard',
                           materials=cur_materials)


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
