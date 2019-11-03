from flask import Blueprint
from flask import render_template
from flask import request
from flask import session
from flask import jsonify

import re
import json

from app.auth import UserRole
from app.auth import at_least_role
from app.db_manager import sqliteManager as db
from app.queries import queries

import config


mark = Blueprint('mark', __name__)


@mark.route('/mark', methods=['GET', 'POST'])
@at_least_role(UserRole.PUBLIC)
def mark_submission():
    if request.method == 'GET':
        return render_template('mark_submission.html',
                               topic_request_text=config.TOPIC_REQUEST_TEXT,
                               heading='Mark Submission',
                               title='Mark Submission')
