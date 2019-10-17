from flask import Flask
from flask import g

from app.auth import auth
from app.home import home

import config


app = Flask(__name__)
app.secret_key = config.SECRET_KEY

for blueprint in [auth, home]:
    app.register_blueprint(blueprint)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    if config.DEBUG:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(use_reloader=True, debug=config.DEBUG)
