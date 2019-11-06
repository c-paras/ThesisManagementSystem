from flask import Flask

from os import path

from app.auth import auth
from app.create_task import create_task
from app.create_topic import create_topic
from app.db_manager import sqliteManager as db
from app.errors import errors
from app.home import home
from app.manage_courses import manage_courses
from app.mark import mark
from app.manage_topics import manage_topics
from app.request_topic import request_topic
from app.search import search
from app.submission import submissions
from app.tasks import tasks


import config


app = Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.teardown_appcontext
def close_connection(exception):
    db.close(exception)


def init_app():
    blueprints = [
        auth, home, errors, create_topic, search, request_topic,
        tasks, manage_topics, create_task, submissions, mark, manage_courses
    ]

    # register blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    def file_exists(filename):
        return path.isfile(filename)

    # set up custom jinja filters
    app.jinja_env.filters['file_exists'] = file_exists


if __name__ == '__main__':
    if config.DEBUG:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    init_app()
    app.run(use_reloader=True, debug=config.DEBUG)
