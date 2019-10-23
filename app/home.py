from flask import Blueprint
from flask import render_template
from flask import session

from app.auth import loggedin
from app.db_manager import sqliteManager as db


home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def index():
    if 'user' not in session:
        return render_template('login.html', title='Login', hide_navbar=True)
    else:
        return dashboard()


@home.route('/home', methods=['GET'])
@home.route('/dashboard', methods=['GET'])
@loggedin
def dashboard():
    is_student = session['acc_type'] == 'student'
    if(is_student):
        return student_dashboard()
    else:
        return staff_dashboard()


def student_dashboard():
    return render_template('homeStudent.html',
                           heading='My Dashboard', title='My Dashboard')


def staff_dashboard():
    db.connect()

    curr_requests = db.customQuery("""
                                        SELECT stu.name, stu.name, t.name
                                        FROM users stu
                                        INNER JOIN topic_requests tr
                                            ON stu.id = tr.student
                                        INNER JOIN topics t
                                            ON t.id = tr.topic
                                        INNER JOIN users sup
                                            ON t.supervisor = sup.id
                                        INNER JOIN request_statuses rs
                                            ON tr.status = rs.id
                                        WHERE sup.email = "{my_email}"
                                            AND rs.name = "pending";
                                   """.format(my_email=session["user"]))
    print(curr_requests)

    # need to implement way of deciding between current and past students, best
    # way would probably be by testing start/end date and current unix
    # timestamp. Need to wait until 'user_session' table is filled before
    # this is possible.

    curr_students = []
    # get current students who I am supervising
    curr_super_students = db.customQuery("""
                                        SELECT stu.name, stu.name, t.name
                                        FROM users stu
                                        INNER JOIN student_topic st
                                            ON st.student = stu.id
                                        INNER JOIN topics t
                                            ON t.id = st.topic
                                        INNER JOIN users sup
                                            ON sup.id = t.supervisor
                                        WHERE sup.email = "{my_email}";
                                   """.format(my_email=session["user"]))
    for tup_student in curr_super_students:
        i = list(tup_student)
        i.append("Supervisor")
        curr_students.append(i)

    # get current students who I am asessing
    curr_assess_students = db.customQuery("""
                                            SELECT stu.name, stu.name, t.name
                                            FROM users stu
                                            INNER JOIN student_topic st
                                                ON st.student = stu.id
                                            INNER JOIN topics t
                                                ON t.id = st.topic
                                            INNER JOIN users sup
                                                ON sup.id = st.assessor
                                            WHERE sup.email = "{my_email}";
                                          """.format(my_email=session["user"]))
    for i in curr_assess_students:
        i = list(tup_student)
        i.append("Assessor")
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
