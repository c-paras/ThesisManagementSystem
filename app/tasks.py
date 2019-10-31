from flask import abort
from flask import Blueprint
from flask import render_template
from flask import session
from flask import request

from datetime import datetime
import calendar

from app.auth import UserRole
from app.auth import at_least_role
from app.queries import queries
from app.db_manager import sqliteManager as db


tasks = Blueprint('tasks', __name__)


@tasks.route('/view_task', methods=['GET'])
@at_least_role(UserRole.STUDENT)
def view_task():
    user_type = session['acc_type']

    if user_type == 'student':
        return student_view()
    else:
        return staff_view()


def student_view():
    db.connect()
    task_id = int(request.args.get('task', None))

    # check that this user is allowed to view this task
    canView = False
    my_tasks = queries.get_user_tasks(session['id'])
    for task in my_tasks:
        if task[0] == int(task_id):
            canView = True
            break

    if not canView:
        print("Can't find "+str(task_id))
        abort(403)

    #
    # get general page info
    #

    task_info = queries.get_general_task_info(task_id)[0]

    # get deadline
    time_format = '%d/%m/%Y at %I:%M:%S %p'
    due_date = datetime.fromtimestamp(task_info[2])
    weekday = calendar.day_name[datetime.fromtimestamp(task_info[2]).weekday()]

    deadline_text = weekday + " " + due_date.strftime(time_format)

    #
    # get criteria & marks
    #

    staff_marks = {}

    # get supervisor's marks

    res = queries.get_students_supervisor(session['id'])
    staff_marks["Supervisor"] = get_marks_table(session['id'],
                                                res,
                                                task_id)

    res = queries.get_students_assessor(session['id'])
    staff_marks["Assessor"] = get_marks_table(session['id'],
                                              res,
                                              task_id)

    print(staff_marks)

    db.close()
    return render_template('task_student.html',
                           heading=task_info[0] + " - " + task_info[1],
                           title=task_info[1],
                           deadline=deadline_text,
                           description=task_info[3],
                           is_text_task=task_info[4] == "text submission",
                           staff_marks=staff_marks)


# get a nicely formatted table containing the marks of a student, or a blank
# list of the criteria
def get_marks_table(student_id, staff_query, task_id):

    # check if staffmember is assigned to this student, else return blank list
    if not len(staff_query):
        return []

    staff_id = staff_query[0][0]
    res = queries.get_marks_table(student_id, staff_id, task_id)

    # check if any marks were returned, if so return those marks
    print(res)
    if len(res):
        return res

    # otherwise build a table of the criteria
    default_criteria = queries.get_task_criteria(task_id)
    ret_list = []
    for criteria in default_criteria:
        ret_list.append([criteria[0], '-', criteria[1], '-'])

    return ret_list


def staff_view():
    abort(404)  # TODO: add staff version of task page
