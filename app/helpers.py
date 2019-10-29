import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import jsonify

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


def send_email(to, subject, body):
    '''
    Send an email to the specified address.
    '''

    # Construct email
    msg = MIMEMultipart()
    msg['From'] = config.SYSTEM_EMAIL
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email over SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config.SYSTEM_EMAIL, config.SYSTEM_PASSWORD)
    server.sendmail(config.SYSTEM_EMAIL, to, msg.as_string())
    server.quit()
