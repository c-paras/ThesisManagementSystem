from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from datetime import datetime

from app.auth import at_least_role
from app.auth import UserRole
from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload
from app.helpers import error, timestamp_to_string, zid_sort
from app.queries import queries
from app.helpers import send_email

import json
import sqlite3

import config


tasks = Blueprint('tasks', __name__)


@tasks.route('/view_task', methods=['GET'])
@at_least_role(UserRole.STUDENT)
def view_task():
    task_id = request.args.get('task', None, type=int)
    if task_id is None:
        abort(400)

    student = {
        'id': None,
        'supervisor': {},
        'assessor': {}
    }
    if session['acc_type'] == 'student':
        student['id'] = session['id']
    else:
        student['id'] = request.args.get('student', None, type=int)

    if not student['id']:
        abort(400)

    db.connect()

    student['supervisor'], student['assessor'] =\
        get_students_staff(student['id'])

    res = db.select_columns('users', ['name', 'email'],
                            ['id'], [student['id']])
    if not res:
        db.close()
        abort(404)
    student['name'] = res[0][0]
    student['email'] = res[0][1]

    # check that this user is allowed to view this task
    can_view = False
    my_tasks = queries.get_user_tasks(student['id'])
    for task in my_tasks:
        if task[0] == task_id:
            can_view = True
            break

    if not can_view:
        db.close()
        abort(403)
    #
    # get general page info
    #

    task = build_task(task_id)

    can_submit = datetime.now().timestamp() <= task['deadline']
    accepted_files = None
    if 'text' not in task['sub_method']['name']:
        accepted_files = ','.join(queries.get_tasks_accepted_files(task_id))

    #
    # get criteria & marks
    #
    mark_details = {}
    approval_feedback = ''

    if 'approval' in task['mark_method']['name']:
        res = queries.get_submission_status(student['id'], task_id)

        feedback1 = None
        if student['supervisor']:
            feedback1 = get_marks_table_with_default(
                student['id'],
                student['supervisor'],
                task_id)[0][3]

        feedback2 = None
        if student['assessor']:
            feedback2 = get_marks_table_with_default(
                student['id'],
                student['assessor'],
                task_id)

        if feedback2:
            feedback2 = feedback2[0][3]
        if feedback1 != 'Awaiting Marking':
            approval_feedback = feedback1
        elif feedback2 != 'Awaiting Marking':
            approval_feedback = feedback2
    else:
        mark_details["Supervisor"] = []
        if student['supervisor']:
            mark_details["Supervisor"] = get_marks_table_with_default(
                student['id'],
                student['supervisor'],
                task_id)

        mark_details["Assessor"] = []
        if student['assessor']:
            mark_details["Assessor"] = get_marks_table_with_default(
                student['id'],
                student['assessor'],
                task_id)

    submission = build_student_submission(student['id'], task_id)

    db.close()

    owner = session['id'] == student['id']
    return render_template('task_base.html',
                           heading=task['course_name'] + " - " + task['name'],
                           title=task['name'],
                           task=task,
                           accepted_files=accepted_files,
                           mark_details=mark_details,
                           approval_feedback=approval_feedback,
                           submission=submission,
                           task_id=task_id,
                           max_size=task['file_limit'],
                           can_submit=can_submit,
                           owner=owner,
                           student=student,
                           marker=False)


# get a nicely formatted table containing the marks of a student, or a blank
# list of the criteria in the case of no submission
def get_marks_table_with_default(student_id, staff_id, task_id):
    res = queries.get_marks_table(student_id, staff_id, task_id)
    # check if any marks were returned, if so return those marks
    if res:
        return res
    default_criteria = queries.get_task_criteria(task_id)
    ret_list = []
    for criteria in default_criteria:
        ret_list.append([criteria[0], '-', criteria[1], 'Awaiting Marking'])

    return ret_list


@tasks.route('/mark_task', methods=['GET', 'POST'])
@at_least_role(UserRole.STAFF)
def mark_task():
    if request.method == 'GET':
        task_id = request.args.get('task', None, type=int)
        student_id = request.args.get('student', None, type=int)
        if task_id is None or student_id is None:
            abort(400)
        db.connect()

        if session['id'] not in get_students_staff(student_id):
            db.close()
            abort(403)

        task = build_task(task_id)
        if not task:
            db.close()
            abort(404)

        res = db.select_columns('users', ['name', 'email'],
                                ['id'], [student_id])
        if not res:
            db.close()
            abort(404)
        student = {
            'id': student_id,
            'name': res[0][0],
            'email': res[0][1]
        }

        task_criteria = db.select_columns('task_criteria',
                                          ['id', 'task', 'name', 'max_mark'],
                                          ['task'], [task_id])

        submission = build_student_submission(student_id, task_id)

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

        check_if_assessor = db.select_columns('student_topic', ['student'],
                                              ['assessor', 'student'],
                                              [session['id'], student_id])
        is_assessor = False
        if check_if_assessor:
            is_assessor = True
        db.close()

        heading = f"{task['course_name']} - {task['name']}"

        return render_template('task_base.html',
                               topic_request_text=config.TOPIC_REQUEST_TEXT,
                               heading=heading,
                               title=task['name'],
                               taskCriteria=task_criteria,
                               student=student,
                               submission=submission,
                               studentId=student_id,
                               taskCriteriaId=task_criteria_id,
                               taskMax=task_max,
                               markedFeedback=marked_feedback,
                               task=task,
                               marker=True,
                               isAssessor=is_assessor)

    data = json.loads(request.data)
    marks = data['marks']
    feedback = data['feedback']
    task_id = data['taskId']
    student_id = data['studentId']
    task_criteria = data['taskCriteria']
    task_max = data['taskMax']
    db.connect()
    if session['id'] not in get_students_staff(student_id):
        db.close()
        abort(403)

    try:
        check = data['approveCheck']
        if (not check):
            res = db.select_columns('request_statuses',
                                    ['id'], ['name'], ['rejected'])
            db.update_rows('submissions', [res[0][0]],
                           ['status'],
                           ['student', 'task'],
                           [student_id, task_id])
        else:
            res = db.select_columns('request_statuses',
                                    ['id'], ['name'], ['approved'])
            db.update_rows('submissions', [res[0][0]],
                           ['status'],
                           ['student', 'task'],
                           [student_id, task_id])

        marks = [100]

        if feedback[0] == '':
            feedback = [None]

    except KeyError:
        pass

    for i in range(len(marks)):
        try:
            val = int(marks[i])
            if val < 0 or val > 100:
                db.close()
                return error('Marks must be between 0-100')

            if val > task_max[i]:
                db.close()
                return error(f'Mark {val} exceeds max mark of {task_max[i]}')
        except ValueError:
            db.close()
            return error('Please enter an integer value for marks')

    for f in feedback:
        if f == '':
            db.close()
            return error('Please enter some feedback')

    for i in range(len(marks)):
        try:
            db.insert_single(
                'marks',
                [task_criteria[i], student_id,
                 session['id'], marks[i], feedback[i]],
                ['criteria', 'student', 'marker', 'mark', 'feedback']
            )
        except sqlite3.IntegrityError:
            db.update_rows('marks', [marks[i], feedback[i]],
                           ['mark', 'feedback'],
                           ['criteria', 'student', 'marker'],
                           [task_criteria[i], student_id, session['id']])

    marked_method = db.select_columns('marking_methods', ['id'],
                                      ['name'], ["requires mark"])[0][0]
    is_mark_type = len(db.select_columns('tasks', ['id'],
                                         ['id', 'marking_method'],
                                         [task_id, marked_method]))

    if is_mark_type:
        new_sub_status = "pending mark"
        if queries.is_fully_marked(student_id, task_id):
            new_sub_status = "marked"
        elif queries.is_partially_marked(student_id, task_id):
            new_sub_status = "partially marked"

        status_id = db.select_columns('request_statuses', ['id'],
                                      ['name'], [new_sub_status])[0][0]

        db.update_rows('submissions',
                       [status_id],
                       ['status'],
                       ['student', 'task'],
                       [student_id, task_id])

    # send email
    student = db.select_columns('users', ['name', 'email'],
                                ['id'], [student_id])[0]
    task_name = db.select_columns('tasks', ['name'], ['id'], [task_id])[0][0]
    marker = session['name']
    subject = f'Marks Entered for Task "{task_name}"'
    msg1 = f'Your submission for task "{task_name}"' + \
           f' has just been marked by {marker}.'
    view_link = url_for('.view_task', task=task_id, _external=True)
    msg2 = f'You can view your marks and feedback ' + \
           f'<a href="{view_link}">here</a>.'
    send_email(to=student[1], name=student[0], subject=subject,
               messages=[msg1, msg2])

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


def get_students_staff(student_id):
    res = queries.get_students_supervisor(student_id)
    supervisor = None
    if res:
        supervisor = res[0][0]

    assessor = None
    res = queries.get_students_assessor(student_id)
    if res:
        assessor = res[0][0]
    return (supervisor, assessor)


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

    task = build_task(task_id)
    res = db.select_columns('enrollments', ['user'],
                            ['user', 'course_offering'],
                            [session['id'], task['offering']])
    if not res:
        db.close()
        return error("User not enrolled in task's course")

    if not request.form.get('certify', 'false') == 'true':
        db.close()
        return error("You must certify this is all your own work")

    if datetime.now().timestamp() >= task['deadline']:
        db.close()
        return error("Submissions closed!<br>You can no longer submit")

    if task['mark_method']['name'] == 'requires approval':
        res = db.select_columns('request_statuses', ['id'],
                                ['name'], ['pending'])
    elif task['mark_method']['name'] == 'requires mark':
        res = db.select_columns('request_statuses', ['id'],
                                ['name'], ['pending mark'])
    pending_status_id = res[0][0]

    try:
        sent_file = FileUpload(req=request)
    except KeyError:
        db.close()
        return error("You must supply a file for submission")

    if sent_file.get_extention() not in task['accepted_files']:
        db.close()
        accept_files = ', '.join([f[1:] for f in task['accepted_files']])
        return error(f"File must be formatted as {accept_files}")
    if sent_file.get_size() > task['file_limit']:
        sent_file.remove_file()
        db.close()
        return error(
            f'File exceeds the maximum size of {task["file_limit"]} MB')

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
                                     pending_status_id],
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
    task = build_task(task_id)

    res = db.select_columns('enrollments', ['user'],
                            ['user', 'course_offering'],
                            [session['id'], task['offering']])
    if not res:
        db.close()
        return error("User not enrolled in task's course")

    if not request.form.get('certify', 'false') == 'true':
        db.close()
        return error("You must certify this is all your own work")

    if datetime.now().timestamp() >= task['deadline']:
        db.close()
        return error("Submissions closed!<br>You can no longer submit")

    mark_method_id = None
    if task['mark_method']['name'] == 'requires approval':
        mark_method_id = db.select_columns('request_statuses', ['id'],
                                           ['name'], ['pending'])[0][0]
    elif task['mark_method']['name'] == 'requires mark':
        mark_method_id = db.select_columns('request_statuses', ['id'],
                                           ['name'], ['pending mark'])[0][0]

    # check if text is too long
    if(len(text.strip().split(' ')) > task["word_limit"]):
        db.close()
        return error(f'Your submission exceeds the word limit')

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


@tasks.route('/task_info', methods=['GET'])
@at_least_role(UserRole.COURSE_ADMIN)
def task_info():
    db.connect()
    task_id = request.args.get('task_id', None, type=int)
    if not task_id:
        db.close()
        return abort(400)
    task = build_task(task_id)
    if not task:
        db.close()
        return abort(404)

    students = get_student_statuses(task)
    for s in students:
        if s['submission_date']:
            s['submission_date'] = timestamp_to_string(s['submission_date'])
    db.close()
    students.sort(key=lambda x: zid_sort(x['email']))
    return render_template('task_stats.html',
                           task=task,
                           students=students,
                           heading=f"{task['name']} - Statistics",
                           title=f"{task['name']} - Statistics")


@tasks.route('/task_status', methods=['GET'])
@at_least_role(UserRole.COURSE_ADMIN)
def task_status():
    db.connect()
    task = build_task(request.args.get('task_id', -1, type=int))
    if not task:
        db.close()
        return error("Could not find task")
    students = get_student_statuses(task)
    db.close()
    return jsonify({'status': 'ok', 'students': students})


def get_student_statuses(task):
    res = db.select_columns('enrollments', ['user'],
                            ['course_offering'], [task['offering']])
    students = [{'id': r[0]} for r in res]
    for student in students:
        res = db.select_columns('users', ['name', 'email'],
                                ['id'], [student['id']])
        student['name'] = res[0][0]
        student['email'] = res[0][1]

        res = db.select_columns('submissions',
                                ['date_modified', 'status'],
                                ['task', 'student'],
                                [task['id'], student['id']])
        submissions = [{'date': r[0], 'status': {'id': r[1]}} for r in res]
        if not submissions:
            student['submission_date'] = None
            student['status'] = {'id': -1, 'name': 'not submitted'}
        else:
            # We only support one submission at a time
            student['submission_date'] = submissions[0]['date']
            res = db.select_columns('request_statuses', ['name'],
                                    ['id'], [submissions[0]['status']['id']])
            submissions[0]['status']['name'] = res[0][0]
            student['status'] = submissions[0]['status']
    return students


def build_task(task_id):
    'Assumes you already have a database connection open'
    res = db.select_columns('tasks', ['deadline', 'marking_method',
                                      'visible', 'course_offering',
                                      'word_limit', 'name',
                                      'description', 'submission_method',
                                      'word_limit', 'size_limit'],
                            ['id'], [task_id])
    if not res:
        return None

    task = {
        'id': task_id,
        'deadline': res[0][0],
        'pretty_deadline': timestamp_to_string(res[0][0], True),
        'mark_method': {
            'id': res[0][1]
        },
        'sub_method': {
            'id': res[0][7]
        },
        'visible': res[0][2],
        'offering': res[0][3],
        'word_limit': res[0][4],
        'name': res[0][5],
        'description': res[0][6],
        'text_limit': res[0][8],
        'file_limit': res[0][9],
        'attachment': None,
        'accepted_files': queries.get_tasks_accepted_files(task_id)
    }
    res = queries.get_general_task_info(task_id)
    task['course_name'] = res[0][0]

    res = db.select_columns('marking_methods', ['name'],
                            ['id'], [task['mark_method']['id']])
    task['mark_method']['name'] = res[0][0]

    res = db.select_columns('submission_methods', ['name'],
                            ['id'], [task['sub_method']['id']])
    task['sub_method']['name'] = res[0][0]

    res = db.select_columns('task_attachments', ['path'], ['task'], [task_id])
    if res:
        task['attachment'] = FileUpload(filename=res[0][0])
    return task


def build_student_submission(student_id, task_id):
    res = db.select_columns('submissions', ['name', 'path', 'text',
                                            'date_modified', 'status'],
                            ['student', 'task'], [student_id, task_id])
    # Account for no submission and a text based submission (no path)
    if not res:
        return {}
    submission = {
        'name': res[0][0],
        'date_modified': timestamp_to_string(res[0][3], True),
        'status': {
            'id': res[0][4]
        },
        'file': None,
        'text': None
    }

    task = build_task(task_id)
    if 'file' in task['sub_method']['name']:
        submission['file'] = FileUpload(filename=res[0][1])
    else:
        submission['text'] = res[0][2]

    res = db.select_columns('request_statuses',
                            ['name'], ['id'],
                            [submission['status']['id']])
    submission['status']['name'] = res[0][0]
    if 'approval' in task['mark_method']['name']:
        submission['mark_method'] = 'approval'
    else:
        submission['mark_method'] = 'mark'
    return submission
