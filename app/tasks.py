from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from flask import session

from datetime import datetime

from app.auth import at_least_role
from app.auth import UserRole
from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload
from app.helpers import error, timestamp_to_string
from app.queries import queries
from app.helpers import send_email

import calendar
import json
import sqlite3

import config


tasks = Blueprint('tasks', __name__)


@tasks.route('/view_task', methods=['GET', 'POST'])
@at_least_role(UserRole.STUDENT)
def view_task():
    user_type = session['acc_type']

    if user_type == 'student':
        return student_view()
    else:
        return staff_view()


def student_view():
    task_id = request.args.get('task', None, type=int)
    if task_id is None:
        abort(400)
    db.connect()

    # check that this user is allowed to view this task
    can_view = False
    my_tasks = queries.get_user_tasks(session['id'])
    for task in my_tasks:
        if task[0] == task_id:
            can_view = True
            break

    if not can_view:
        abort(403)

    #
    # get general page info
    #

    task_info = queries.get_general_task_info(task_id)[0]

    can_submit = datetime.now().timestamp() <= task_info[2]
    text_submission = task_info[4] == "text submission"
    accepted_files = None
    if not text_submission:
        accepted_files = ','.join(queries.get_tasks_accepted_files(task_id))
    # get deadline

    deadline_text = timestamp_to_string(task_info[2], True)

    #
    # get criteria & marks
    #
    is_approval = (task_info[5] == 'requires approval')
    awaiting_marks = False
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
        if not (type(mark_details["Supervisor"]) == () and
                type(mark_details["Assessor"]) == ()):
            awaiting_marks = True

    attachment = None
    res = db.select_columns('task_attachments', ['path'], ['task'], [task_id])
    if res:
        attachment = FileUpload(filename=res[0][0])
    prev_submission = None
    # check if the student needs to submit
    res = db.select_columns('submissions',
                            ['name', 'path', 'date_modified'],
                            where_col=['student', 'task'],
                            where_val=[session['id'], task_id])

    if res:
        try:
            prev_submission = {
                'name': res[0][0],
                'modify_date': timestamp_to_string(res[0][2], True)
            }
        except LookupError as e:
            print(f"Submission {task_id} {session['user']}: {e}")

    if prev_submission and task_info[4] == "file submission":
        prev_submission['url'] = FileUpload(filename=res[0][1]).get_url()

    text_info = {}
    if task_info[4] == "text submission":
        text_info["limit"] = task_info[7]
        text_info["button_text"] = "Start Submission"

        res = db.select_columns('submissions', ['text', 'date_modified'],
                                where_col=['student', 'task'],
                                where_val=[session['id'], task_id])
        if res:
            text_info["old_text"] = res[0][0]
            text_info["edited_time"] = timestamp_to_string(res[0][1])
            text_info["button_text"] = "Edit Submission"

    db.close()
    return render_template('task_base.html',
                           heading=task_info[0] + " - " + task_info[1],
                           title=task_info[1],
                           deadline_text=deadline_text,
                           description=task_info[3],
                           text_info=text_info,
                           accepted_files=accepted_files,
                           mark_details=mark_details,
                           prev_submission=prev_submission,
                           is_approval=is_approval,
                           task_id=task_id,
                           max_size=task_info[6],
                           attachment=attachment,
                           can_submit=can_submit,
                           awaiting_marks=awaiting_marks)


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
    if request.method == 'GET':
        task_id = request.args.get('task', None, type=int)
        student_id = request.args.get('student', None, type=int)
        if task_id is None or student_id is None:
            abort(400)
        db.connect()
        task_info = queries.get_general_task_info(task_id)
        if not task_info:
            db.close()
            abort(404)
        else:
            task_info = task_info[0]
        student_details = db.select_columns('users', ['name', 'email'],
                                            ['id'], [student_id])
        if not student_details:
            db.close()
            abort(404)

        # get deadline

        deadline_text = timestamp_to_string(task_info[2], True)

        res = queries.get_material_and_attachment(task_id)
        attachment = None
        if res:
            attachment = FileUpload(filename=res[0][0])

        task_criteria = db.select_columns('task_criteria',
                                          ['id', 'task', 'name', 'max_mark'],
                                          ['task'], [task_id])

        student_email = student_details[0][1].split('@')[0]
        res = db.select_columns('submissions',
                                ['name', 'path', 'text', 'date_modified'],
                                ['student', 'task'],
                                [student_id, task_id])
        submission = {}
        # Account for no submission and a text based submission (no path)
        if res:
            submission['name'] = res[0][0]
            submission['date_modified'] = datetime.fromtimestamp(res[0][3])
            if res[0][1] is not None:
                submission['file'] = FileUpload(filename=res[0][1])
            else:
                submission['text'] = res[0][2]
                status = db.select_columns('submissions', ['status'],
                                           ['student', 'task'],
                                           [student_id, task_id])[0][0]
                submission['status'] = db.select_columns('request_statuses',
                                                         ['name'], ['id'],
                                                         [status])[0][0]

        if 'approval' in task_info[5]:
            submission['markingMethod'] = 'approval'
        else:
            submission['markingMethod'] = 'mark'

        marked_feedback = []
        for criteria in task_criteria:
            marked_feedback.append(
                db.select_columns('marks',
                                  ['mark', 'feedback'],
                                  ['criteria', 'student', 'marker'],
                                  [criteria[0], student_id, session['id']]))

        task_criteria_id = []
        for criteria in task_criteria:
            task_criteria_id.append(criteria[0])

        task_max = []
        for criteria in task_criteria:
            task_max.append(criteria[3])

        db.close()
        return render_template('task_base.html',
                               topic_request_text=config.TOPIC_REQUEST_TEXT,
                               heading=task_info[0] + " - " + task_info[1],
                               title=task_info[1],
                               deadline_text=deadline_text,
                               description=task_info[3],
                               attachment=attachment,
                               taskCriteria=task_criteria,
                               studentName=student_details[0][0],
                               studentEmail=student_email,
                               submission=submission,
                               studentId=student_id,
                               taskCriteriaId=task_criteria_id,
                               taskMax=task_max,
                               markedFeedback=marked_feedback,
                               staffUser=True)

    data = json.loads(request.data)
    marks = data['marks']
    feedback = data['feedback']
    task_id = data['taskId']
    studentId = data['studentId']
    task_criteria = data['taskCriteria']
    task_max = data['taskMax']

    db.connect()
    try:
        check = data['approveCheck']
        if (not check):
            res = db.select_columns('request_statuses',
                                    ['id'], ['name'], ['pending'])
            db.update_rows('submissions', [res[0][0]],
                           ['status'],
                           ['student', 'task'],
                           [studentId, task_id])
        else:
            res = db.select_columns('request_statuses',
                                    ['id'], ['name'], ['approved'])
            db.update_rows('submissions', [res[0][0]],
                           ['status'],
                           ['student', 'task'],
                           [studentId, task_id])

        marks = [100]

        if feedback[0] == '':
            feedback = [None]

    except KeyError:
        pass

    for i in range(len(marks)):
        try:
            val = int(marks[i])
            if val < 0 or val > 100:
                return jsonify({'status': 'fail',
                                'message':
                                'Marks must be between 0-100'})

            if val > task_max[i]:
                return jsonify({'status': 'fail',
                                'message':
                                'Marks exceeds max mark'})
        except ValueError:
            return jsonify({'status': 'fail',
                            'message':
                            'Please enter a integer value for marks'})

    for f in feedback:
        if f == '':
            return jsonify({'status': 'fail',
                            'message': 'Please enter some feedback'})

    for i in range(len(marks)):
        try:
            db.insert_single(
                'marks',
                [task_criteria[i], studentId,
                 session['id'], marks[i], feedback[i]],
                ['criteria', 'student', 'marker', 'mark', 'feedback']
            )
        except sqlite3.IntegrityError:
            db.update_rows('marks', [marks[i], feedback[i]],
                           ['mark', 'feedback'],
                           ['criteria', 'student', 'marker'],
                           [task_criteria[i], studentId, session['id']])

    res = db.select_columns('users', ['name', 'email'], ['id'], [studentId])

    send_email(to=res[0][1], name=res[0][0], subject="Marks Released",
               messages=['Your submission has been marked'])

    db.close()
    return jsonify({'status': 'ok'})


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
                                     str(sent_file.get_name()),
                                     datetime.now().timestamp(),
                                     mark_method_id],
                     ['student', 'task', 'name', 'path',
                      'date_modified', 'status'])
    db.close()
    return jsonify({'status': 'ok'})


@tasks.route('/submit_text_task', methods=['POST'])
@at_least_role(UserRole.STUDENT)
def submit_text_task():
    task_id = request.form.get('task', -1)
    text = request.form.get('text-submission', -1)

    db.connect()
    res = db.select_columns('tasks', ['deadline', 'marking_method',
                                      'visible', 'course_offering',
                                      'word_limit', 'name'],
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
        'word_limit': res[0][4],
        'name': res[0][5]
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

    # check if text is too long
    if(len(text.strip().split(' ')) > task["word_limit"]):
        db.close()
        return error("Your submission is above the word limit")

    res = db.select_columns('submissions', ['*'], ['student', 'task'],
                            [session['id'], task['id']])
    if res:
        # if there's already a submission, delete it
        db.delete_rows('submissions', ['student', 'task'],
                       [session['id'], task['id']])

    db.insert_single('submissions', [session['id'], task['id'],
                                     task['name'],
                                     text,
                                     datetime.now().timestamp(),
                                     mark_method_id],
                     ['student', 'task', 'name', 'text',
                      'date_modified', 'status'])
    db.close()
    return jsonify({'status': 'ok'})
