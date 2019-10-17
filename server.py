from flask import Flask
from flask import g

from app.auth import auth

import config


app = Flask(__name__)
app.register_blueprint(auth)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    if config.DEBUG:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(use_reloader=True, debug=config.DEBUG)
