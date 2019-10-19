from flask import Flask
from flask import g

from app.auth import auth
from app.home import home
from app.errors import errors
from app.db_manager import sqliteManager as db

import config


app = Flask(__name__)
app.secret_key = config.SECRET_KEY

for blueprint in [auth, home, errors]:
    app.register_blueprint(blueprint)


@app.teardown_appcontext
def close_connection(exception):
    db.close(exception)


if __name__ == '__main__':
    if config.DEBUG:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(use_reloader=True, debug=config.DEBUG)
