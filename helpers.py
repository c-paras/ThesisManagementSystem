from flask import g
from flask import jsonify

import sqlite3

import config


def get_db():
    '''
    Connect to sqlite3 database.
    '''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config.DATABASE)
    return db


def get_fields(form, fields):
    '''
    Retrieve field data from form, raising an exception in the case
    that at least one field is blank.
    '''
    data = []
    for field in fields:
        value = form.get(field, None)
        if value is None or len(value) is 0:
            field_name = field.capitalize()
            err = jsonify({'status': 'fail',
                           'message': f'{field_name} cannot be blank!'})
            raise ValueError(err)
        data.append(value)
    return data
