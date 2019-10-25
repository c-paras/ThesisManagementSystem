from flask import jsonify


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
            plural = 'are' if field_name.endswith('s') else 'is'
            err = error(f'{field_name} {plural} required!')
            raise ValueError(err)
        data.append(value)
    return data


def error(msg):
    ''' Format error response with message. '''
    if not (msg.endswith('.') or msg.endswith('!')):
        msg += '!'
    return jsonify({'status': 'fail', 'message': msg})
