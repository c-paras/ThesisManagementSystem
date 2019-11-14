from flask import abort
from flask import Blueprint
from flask import render_template
from flask import session
from flask import request

from datetime import datetime

from app.auth import at_least_role
from app.auth import UserRole
from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload
from app.queries import queries
from app.helpers import timestamp_to_string

import calendar


submissions = Blueprint('submissions', __name__)


@submissions.route('/view_submission', methods=['GET'])
@at_least_role(UserRole.STAFF)
def view_submission():
    student_id = request.args.get('submissions', None, type=int)
    if student_id is None:
        abort(400)
    db.connect()
    student_info = db.select_columns('users', ['name', 'email'],
                                     ['id'],
                                     [student_id])
    if not len(student_info):
        db.close()
        abort(404)

    # get tasks for this student
    tasks = []
    student_tasks = queries.get_student_submissions(student_id)
    for task in student_tasks:

        submit_date_text = timestamp_to_string(task[4], True)

        file_url = None
        if task[3]:
            file_url = FileUpload(filename=task[3]).get_url()

        status = get_sub_status(student_id, task[0])
        if 'approval' in task[2]:
            tasks.append((
                task[1], submit_date_text, status, file_url,
                task[0], student_id))

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
                file_url, task[0], student_id
            ))

    db.close()
    zid = student_info[0][1].split('@')[0]
    heading = f'Submissions - {student_info[0][0]} ({zid})'
    print(student_id)
    print(student_tasks)
    return render_template('submission_staff.html',
                           heading=heading,
                           title=heading,
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
