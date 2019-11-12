from flask import Blueprint
from flask import render_template
from flask import request
from flask import session
from flask import jsonify

from datetime import datetime

from app.auth import at_least_role
from app.auth import UserRole
from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload
from app.queries import queries
from app.helpers import send_email

import calendar
import json
import sqlite3

import config


mark = Blueprint('mark', __name__)


@mark.route('/mark', methods=['GET', 'POST'])
@at_least_role(UserRole.STAFF)
def mark_submission():
    if request.method == 'GET':
        db.connect()
        task_id = int(request.args.get('task', None))
        student_id = int(request.args.get('student', None))
        task_info = queries.get_general_task_info(task_id)[0]
        # get deadline
        time_format = '%d/%m/%Y at %I:%M:%S %p'
        due_date = datetime.fromtimestamp(task_info[2])
        weekday = \
            calendar.day_name[datetime.fromtimestamp(task_info[2]).weekday()]

        deadline_text = weekday + " " + due_date.strftime(time_format)

        res = queries.get_material_and_attachment(task_id)
        attachment = None
        if res:
            attachment = FileUpload(filename=res[0][0])

        task_criteria = db.select_columns('task_criteria',
                                          ['id', 'task', 'name', 'max_mark'],
                                          ['task'], [task_id])
        student_details = db.select_columns('users', ['name', 'email'],
                                            ['id'], [student_id])

        student_email = student_details[0][1].split('@')[0]
        res = db.select_columns('submissions', ['name', 'path', 'text'],
                                ['student', 'task'],
                                [student_id, task_id])
        submission = {}
        # Account for no submission and a text based submission (no path)
        if res:
            print(res)
            submission['name'] = res[0][0]
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
                print(submission['status'])

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
        return render_template('mark_submission.html',
                               topic_request_text=config.TOPIC_REQUEST_TEXT,
                               heading=task_info[0] + " - " + task_info[1],
                               title=task_info[1],
                               deadline=deadline_text,
                               description=task_info[3],
                               attachment=attachment,
                               taskCriteria=task_criteria,
                               studentName=student_details[0][0],
                               studentEmail=student_email,
                               submission=submission,
                               studentId=student_id,
                               taskCriteriaId=task_criteria_id,
                               taskMax=task_max,
                               markedFeedback=marked_feedback)

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
            print('not checked')
            res = db.select_columns('request_statuses',
                                    ['id'], ['name'], ['pending'])
            print(res)
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

        print(check)
        print(marks)
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
