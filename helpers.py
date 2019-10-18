from flask import g
from flask import jsonify

import sqlite3

import config


def get_fields(form, fields):
    '''
    Retrieve field data from form, raising an exception in the case
    that at least one field is blank.
    '''
    data = []
    for field in fields:
        value = form.get(field, None)
        if value is None or len(value) is 0:
            field_name = field.capitalize().replace('-', ' ')
            err = jsonify({'status': 'fail',
                           'message': f'{field_name} is required!'})
            raise ValueError(err)
        data.append(value)
    return data


def error(msg):
    ''' Format error response with message. '''
    return jsonify({'status': 'fail', 'message': msg})
