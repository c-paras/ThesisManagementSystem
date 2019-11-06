from flask import abort
from flask import Blueprint
from flask import render_template
from flask import jsonify
from flask import session
from flask import request

from werkzeug import secure_filename
from datetime import datetime
import os
import calendar

from app.auth import UserRole
from app.auth import at_least_role
from app.queries import queries
from app.db_manager import sqliteManager as db
from app.helpers import error
from app.file_upload import FileUpload

import config


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
    can_view = False
    my_tasks = queries.get_user_tasks(session['id'])
    for task in my_tasks:
        if task[0] == int(task_id):
            can_view = True
            break

    if not can_view:
        abort(403)

    #
    # get general page info
    #

    task_info = queries.get_general_task_info(task_id)[0]

    text_submission = task_info[4] == "text submission"
    accepted_files = None
    if not text_submission:
        accepted_files = ','.join(queries.get_tasks_accepted_files(task_id))
    # get deadline
    time_format = '%A %d/%m/%Y at %I:%M:%S %p'
    due_date = datetime.fromtimestamp(task_info[2])
    deadline_text = due_date.strftime(time_format)

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

    res = db.select_columns('task_attachments', ['path'], ['task'], [task_id])
    attachments = [FileUpload(filename=r[0]) for r in res]

    # check if the student needs to submit
    res = db.select_columns('submissions', ['name', 'path', 'date_modified'],
                            where_col=['student', 'task'],
                            where_val=[session['id'], task_id])

    prev_submission = None
    if res:
        try:
            prev_submission = {
                'name': res[0][0],
                'url': FileUpload(filename=res[0][1]).get_url(),
                'modify_date': datetime.fromtimestamp(res[0][2])
            }
        except LookupError as e:
            print(f"Submission for task {task_id} for {session['user']}: {e}")

    db.close()
    return render_template('task_student.html',
                           heading=task_info[0] + " - " + task_info[1],
                           title=task_info[1],
                           deadline=deadline_text,
                           description=task_info[3],
                           is_text_task=text_submission,
                           accepted_files=accepted_files,
                           mark_details=mark_details,
                           prev_submission=prev_submission,
                           is_approval=is_approval,
                           task_id=task_id,
                           max_size=task_info[6],
                           attachments=attachments)


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


@tasks.route('/submit_file_task', methods=['POST'])
@at_least_role(UserRole.STUDENT)
def submit_file_task():
    task_id = request.form.get('task', -1)
    db.connect()
    res = db.select_columns('tasks', ['deadline', 'marking_method',
                                      'visible', 'course_offering',
                                      'size_limit'],
                            ['id'], [task_id])
    if not res:
        db.close()
        return error("Task not found")

    task = {
        'id': task_id,
        'deadline': datetime.fromtimestamp(res[0][0]),
        'sub_method': {
            'id': res[0][1]
        },
        'visible': res[0][2],
        'offering': res[0][3],
        'max_size': res[0][4],
        'accepted_files': queries.get_tasks_accepted_files(task_id)
    }

    res = db.select_columns('enrollments', ['user'],
                            ['user', 'course_offering'],
                            [session['id'], task['offering']])
    if not res:
        db.close()
        return error("User not enrolled in task's course")

    if not request.form.get('certify', 'false') == 'true':
        db.close()
        return error("You must certify it is all your own work")

    if datetime.now() >= task['deadline']:
        db.close()
        return error("Submissions closed")

    res = db.select_columns('marking_methods', ['name'],
                            ['id'], [task['sub_method']['id']])
    task['sub_method']['name'] = res[0][0]

    mark_method_id = None
    if task['sub_method']['name'] == 'requires approval':
        mark_method_id = db.select_columns('request_statuses', ['id'],
                                           ['name'], ['pending'])[0][0]
    elif task['sub_method']['name'] == 'requires mark':
        mark_method_id = db.select_columns('request_statuses', ['id'],
                                           ['name'], ['pending mark'])[0][0]

    try:
        sent_file = FileUpload(req=request)
    except KeyError:
        return error("Must give a file for submission")

    if sent_file.get_extention() not in task['accepted_files']:
        db.close()
        accept_files = ', '.join([f[1:] for f in task['accepted_files']])
        return error(f"File must be formatted as {accept_files}")
    if sent_file.get_size() > task['max_size']:
        sent_file.remove_file()
        db.close()
        return error(f"File larger than {task['max_size']}MB")

    sent_file.commit()
    res = db.select_columns('submissions', ['path'], ['student', 'task'],
                            [session['id'], task['id']])
    if res:
        db.delete_rows('submissions', ['student', 'task'],
                       [session['id'], task['id']])
        # If the file doesn't exists don't worry as we are deleting
        # the submission anyway
        try:
            prev_submission = FileUpload(filename=res[0][0])
            prev_submission.remove_file()
        except LookupError:
            pass

    db.insert_single('submissions', [session['id'], task['id'],
                                     sent_file.get_original_name(),
                                     str(sent_file.get_path()),
                                     datetime.now().timestamp(),
                                     mark_method_id],
                     ['student', 'task', 'name', 'path',
                      'date_modified', 'status'])
    db.close()
    return jsonify({})
