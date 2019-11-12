import datetime

from flask import abort
from flask import Flask
from flask import redirect
from flask import url_for

from app.auth import allowed_file_access
from app.auth import auth
from app.db_manager import sqliteManager as db
from app.create_task import create_task
from app.create_topic import create_topic
from app.errors import errors
from app.auth import is_at_least_role
from app.auth import UserRole
from app.home import home
from app.mark import mark
from app.manage_courses import manage_courses
from app.manage_topics import manage_topics
from app.queries import queries
from app.request_topic import request_topic
from app.search import search
from app.submission import submissions
from app.tasks import tasks

import os

import config


class SecureUploadsFlask(Flask):
    def send_static_file(self, filename):
        try:
            if not filename.startswith(config.FILE_UPLOAD_DIR):
                return super(
                    SecureUploadsFlask, self).send_static_file(filename)
            elif allowed_file_access(filename):
                return super(
                    SecureUploadsFlask, self).send_static_file(filename)
            else:
                abort(403)
        except KeyError:
            return redirect(url_for('auth.login'))


app = SecureUploadsFlask(__name__, static_url_path=f'/{config.STATIC_PATH}')
app.secret_key = config.SECRET_KEY


@app.teardown_appcontext
def close_connection(exception):
    db.close(exception)


@app.context_processor
def fill_create_course():
    if not is_at_least_role(UserRole.COURSE_ADMIN):
        return dict()
    db.connect()
    _, end_year = queries.get_year_range()
    start_year = datetime.datetime.now().year
    num_terms = queries.get_terms_per_year(start_year)

    db.close()
    return dict(start_year=start_year, end_year=end_year, num_terms=num_terms)


def init_app():
    blueprints = [
        auth, home, errors, create_topic, search, request_topic,
        tasks, manage_topics, create_task, submissions, mark, manage_courses
    ]

    # register blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    def file_exists(filename):
        return os.path.isfile(filename)

    # set up custom jinja filters
    app.jinja_env.filters['file_exists'] = file_exists


if __name__ == '__main__':
    if config.DEBUG:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    init_app()
    app.run(use_reloader=True, debug=config.DEBUG)
