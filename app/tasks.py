from flask import abort
from flask import Blueprint
from flask import render_template
from flask import session
from flask import request

from datetime import datetime

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
    task_id = int(request.args.get('tID', None))

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

    db.close()
    return render_template('task_student.html',
                           heading='COURSE - TASK',
                           title='PLACEHOLDER')


def staff_view():
    abort(404)  # TODO: add staff version of task page
