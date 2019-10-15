from flask import Flask, render_template, session, request
from flask import Response, url_for, redirect, g
from flask_restful import Resource, Api, reqparse, fields, marshal

import sqlite3
import config


app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template('base.html')  # TODO


if __name__ == '__main__':
    app.run(use_reloader=False, debug=True)
