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
from app.file_upload import FileUpload


submissions = Blueprint('submissions', __name__)


@submissions.route('/view_submission', methods=['GET'])
@at_least_role(UserRole.STUDENT)
def view_submission():
    user_type = session['acc_type']

    if user_type == 'student':
        return student_view()
    else:
        return staff_view()


def staff_view():
    db.connect()
    student_id = int(request.args.get('submissions', None))
    student_info = db.select_columns('users', ['name', 'email'],
                                     ['id'],
                                     [student_id])
    # get tasks for this student
    tasks = []
    student_tasks = queries.get_student_submissions(student_id)
    for task in student_tasks:

        time_format = '%d/%m/%Y at %I:%M:%S %p'
        submit_date = datetime.fromtimestamp(task[4])
        weekday = calendar.day_name[datetime.fromtimestamp(task[4]).weekday()]
        submit_date_text = weekday + " " + submit_date.strftime(time_format)

        status = get_sub_status(student_id, task[0])
        if 'approval' in task[2]:
            tasks.append((
                task[1], submit_date_text, status, task[3]))
        else:
            criteria = db.select_columns(
                'task_criteria', ['id', 'max_mark'], ['task'], [task[0]]
            )

            staff_mark = 0
            total_max_mark = 0
            for c in criteria:
                total_max_mark += c[1]
                mark = db.select_columns(
                    'marks', ['mark'],
                    ['criteria', 'student', 'marker'],
                    [c[0], student_id, session['id']]
                )
                if len(mark) != 0:
                    staff_mark += mark[0][0]
                else:
                    staff_mark = -1
            if staff_mark <= 0:
                staff_mark = '?'
            tasks.append((
                task[1], submit_date_text,
                str(staff_mark) + '/' + str(total_max_mark),
                FileUpload(task[3]).get_url()
            ))

    db.close()
    return render_template('submission_staff.html',
                           heading='View Submissions',
                           title='View Submissions',
                           student=student_info,
                           submissions=tasks)


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


def student_view():
    abort(404)  # TODO: we may have a student version of submission page?


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
