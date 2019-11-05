from flask import Blueprint
from flask import render_template
from flask import request
from flask import session
from flask import jsonify

import re
import json
from datetime import datetime
import calendar

from app.auth import UserRole
from app.auth import at_least_role
from app.db_manager import sqliteManager as db
from app.queries import queries

import config


mark = Blueprint('mark', __name__)


@mark.route('/mark', methods=['GET', 'POST'])
@at_least_role(UserRole.STAFF)
def mark_submission():
    if request.method == 'GET':
        db.connect()
        task_id = int(request.args.get('task', None))
        task_info = queries.get_general_task_info(task_id)[0]
        # get deadline
        time_format = '%d/%m/%Y at %I:%M:%S %p'
        due_date = datetime.fromtimestamp(task_info[2])
        weekday = \
            calendar.day_name[datetime.fromtimestamp(task_info[2]).weekday()]

        deadline_text = weekday + " " + due_date.strftime(time_format)

        material = queries.get_material_and_attachment(task_id)
        task_criteria = db.select_columns('task_criteria',
                                          ['*'], ['task'], [task_id])
        print(material[0][0])
        print(task_criteria)
        return render_template('mark_submission.html',
                               topic_request_text=config.TOPIC_REQUEST_TEXT,
                               heading='Mark Submission',
                               title='Mark Submission',
                               deadline=deadline_text,
                               description=task_info[3],
                               criteria=material[0][0],
                               taskCriteria=task_criteria)
