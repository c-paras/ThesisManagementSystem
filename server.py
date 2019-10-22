from os import path

from flask import Flask
from flask import g

from app.auth import auth
from app.home import home
from app.search import search
from app.errors import errors
from app.db_manager import sqliteManager as db

import config


app = Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.teardown_appcontext
def close_connection(exception):
    db.close(exception)


def init_app():

    # register blueprints
    for blueprint in [auth, home, errors, search]:
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
