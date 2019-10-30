import smtplib

from flask import jsonify
from flask import render_template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread

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


def send_email(to, name, subject, messages):
    '''
    Send an email to the specified address. Use a base template
    for the email structure and attach any messages to the body
    of the HTML email, as well as the person's name and subject.
    '''

    # Construct the email and headers
    msg = MIMEMultipart()
    msg['From'] = config.SYSTEM_EMAIL
    if config.DEBUG:
        print(f'Debugging mode - sending email to {config.SYSTEM_EMAIL}')
        print(f'In production - an email would be sent to {to}')
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
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config.SYSTEM_EMAIL, config.SYSTEM_PASSWORD)
    server.sendmail(config.SYSTEM_EMAIL, to, msg.as_string())
    server.quit()
