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
    is_approval = (task_info[5] == 'requires approval')
    mark_details = {}

    if is_approval:
        res = queries.get_submission_status(session['id'], task_id)

        if len(res) and res[0][0] == "pending":
            mark_details["Approval"] = "Your submission is pending approval."
        elif len(res):
            mark_details["Approval"] = """Your submission has been {status}.
                                       """.format(status=res[0][0])
    else:
        res = queries.get_students_supervisor(session['id'])
        mark_details["Supervisor"] = get_marks_table(session['id'],
                                                     res,
                                                     task_id)

        res = queries.get_students_assessor(session['id'])
        mark_details["Assessor"] = get_marks_table(session['id'],
                                                   res,
                                                   task_id)

    # check if the student needs to submit
    res = db.select_columns('submissions', ['*'],
                            where_col=['student', 'task'],
                            where_val=[session['id'], task_id])

    awaiting_submission = not len(res)
    db.close()
    return render_template('task_student.html',
                           heading=task_info[0] + " - " + task_info[1],
                           title=task_info[1],
                           deadline=deadline_text,
                           description=task_info[3],
                           is_text_task=task_info[4] == "text submission",
                           mark_details=mark_details,
                           awaiting_submission=awaiting_submission,
                           is_approval=is_approval)


# get a nicely formatted table containing the marks of a student, or a blank
# list of the criteria
def get_marks_table(student_id, staff_query, task_id):

    # check if staffmember is assigned to this student, else return blank list
    if not len(staff_query):
        return []

    staff_id = staff_query[0][0]
    res = queries.get_marks_table(student_id, staff_id, task_id)

    # check if any marks were returned, if so return those marks
    if len(res):
        return res

    default_criteria = queries.get_task_criteria(task_id)
    ret_list = []
    for criteria in default_criteria:
        ret_list.append([criteria[0], '-', criteria[1], 'Awaiting Marking'])

    return ret_list


def staff_view():
    abort(404)  # TODO: add staff version of task page