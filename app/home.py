from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for

from app.auth import UserRole
from app.auth import at_least_role
from app.queries import queries


home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    else:
        return dashboard()


@home.route('/home', methods=['GET'])
@home.route('/dashboard', methods=['GET'])
@at_least_role(UserRole.STUDENT)
def dashboard():
    is_student = session['acc_type'] == 'student'
    if is_student:
        return student_dashboard()
    else:
        return staff_dashboard()


def student_dashboard():
    return render_template('homeStudent.html',
                           heading='My Dashboard', title='My Dashboard')


def staff_dashboard():
    curr_requests = queries.get_curr_topic_requests(session['user'])

    # need to implement way of deciding between current and past students, best
    # way would probably be by testing start/end date and current unix
    # timestamp. Need to wait until 'user_session' table is filled before
    # this is possible.

    curr_students = []
    # get current students who I am supervising
    curr_super_students = queries.get_current_super_students(session['user'])

    for tup_student in curr_super_students:
        i = list(tup_student)
        i.append('Supervisor')
        curr_students.append(i)

    # get current students who I am asessing
    curr_assess_students = queries.get_current_assess_students(session['user'])
    for i in curr_assess_students:
        i = list(tup_student)
        i.append('Assessor')
        curr_students.append(i)

    curr_students.extend(curr_assess_students)
    print(curr_students)

    # for now left blank
    past_students = []

    return render_template('homeStaff.html',
                           heading='My Dashboard',
                           title='My Dashboard',
                           curr_requests=curr_requests,
                           curr_students=curr_students,
                           past_students=past_students)
