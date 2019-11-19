from flask import jsonify
from flask import render_template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
from datetime import datetime

import re
import smtplib
import sys

import config


def get_fields(form, fields, optional=None, ints=None):
    '''
    Retrieve field data from form, raising an exception in the case
    that at least one field is blank. Fields marked as optional are
    not checked for being empty. Fields marked as being ints, are
    validated as such and are converted into ints.
    '''
    data = []
    for field in fields:
        value = form.get(field, None)
        field_name = field.capitalize().replace('-', ' ')
        field_name = re.sub(r'^Id', 'ID', field_name)
        field_name = re.sub(r'id$', 'ID', field_name)
        field_name = re.sub(r' id ', ' ID ', field_name)
        if (optional is None or field not in optional) and \
           (value is None or re.match(r'^\s*$', value)):
            plural = 'are' if field_name.endswith('s') else 'is'
            err = error(f'{field_name} {plural} required!')
            raise ValueError(err)
        if ints is not None and field in ints:
            try:
                data.append(int(value))
            except ValueError:
                if optional is not None and field not in optional:
                    err = error(f'{field_name} must be an integer!')
                    raise ValueError(err)
                else:
                    data.append(value)
        else:
            data.append(value)
    return data


def error(msg):
    ''' Format error response with message. '''
    if not (msg.endswith('.') or msg.endswith('!')):
        if '!' in msg:
            msg += '.'
        else:
            msg += '!'
    return jsonify({'status': 'fail', 'message': msg})


def send_email(to, name, subject, messages):
    '''
    Send an email to the specified address. Use a base template
    for the email structure and attach any messages to the body
    of the HTML email, as well as the person's name and subject.
    '''

    if not re.match(r'^.+@.+\..+$', to):
        raise ValueError(f'Invalid email: "{to}"')
    if not type(messages) == list:
        raise TypeError(f'You must supply a list of one or more messages.')

    # Construct the email and headers
    msg = MIMEMultipart()
    msg['From'] = config.SYSTEM_EMAIL

    # Always send email to config.SYSTEM_EMAIL just in case
    print(f'Debugging mode - sending email to {config.SYSTEM_EMAIL}')
    print(f'In production - an email would be sent to {to} ({name})')
    to = config.SYSTEM_EMAIL

    msg['To'] = to
    msg['Subject'] = '{} | TMS'.format(subject)
    msg.add_header('Content-Type', 'text/html')
    body = render_template('email.html', name=name,
                           messages=messages, url=config.SITE_HOME)
    msg.attach(MIMEText(body, 'html'))
    Thread(target=do_email_send, args=[to, msg]).start()


def do_email_send(to, msg):
    '''
    Send an email over SMTP. This function is not meant to be called
    directly. It is invoked by `send_email' in a new thread.
    '''
    if sys._getframe().f_back.f_code.co_name != 'run':
        raise ValueError(
            "Do not call `do_send_email' directly, call `send_email'."
        )

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config.SYSTEM_EMAIL, config.SYSTEM_PASSWORD)
    server.sendmail(config.SYSTEM_EMAIL, to, msg.as_string())
    server.quit()


def timestamp_to_string(timestamp, add_day=False):

    date = datetime.fromtimestamp(timestamp)
    if (add_day):
        print_date = date.strftime("%A %d %b %Y at %H:%M")
    else:
        print_date = date.strftime("%d %b %Y at %H:%M")
    return print_date
