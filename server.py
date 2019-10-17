from flask import Flask, render_template, session, request
from flask import Response, url_for, redirect, g, jsonify
from flask_restful import Resource, Api, reqparse, fields, marshal

from app.auth import auth

import sqlite3
import bcrypt
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
