import csv
import re
import config

from app.db_manager import sqliteManager as db


def get_all_account_types():
    types = {}
    res = db.select_columns('account_types', ['name', 'id'])
    for name, iden in res:
        types[name] = iden
    return types

# expects a csv file in format
# email, new_name, account_type


def update_from_file(path, course_offering=None, default='student'):
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        account_types = get_all_account_types()
        line = 0
        for row in csv_reader:
            line += 1
            clean_row = []
            for i in row:
                temp = i.strip().lower()
                clean_row.append(temp)
            if len(row) < 2:
                error_string = f"Invalid format on line number {line}"
                return error_string
            if not re.match(config.EMAIL_FORMAT, clean_row[0]):
                error_string = f"""Invalid email on line number {line}<br>
                   {config.EMAIL_FORMAT_ERROR}"""
                return error_string
            if len(row) < 3:
                clean_row.append(default)
            account_type = clean_row[2]
            if clean_row[2] in account_types:
                account_type = account_types[clean_row[2]]

            update_account_type(
                clean_row[0], clean_row[1], account_type, course_offering
            )
    return ""


def update_account_type(
        email, new_name, account_type=None, course_offering=None):

    account_types = get_all_account_types()
    course_role = 'staff'
    if account_type is None:
        account_type = 'student'
    if account_type in account_types:
        account_type = account_types[account_type]
    elif account_types['student'] == account_type:
        course_role = 'student'
    res = db.select_columns('course_roles', ['id'], ['name'], [course_role])
    course_role = res[0][0]
    res = db.select_columns('users', ['id'], ['email'], [email])
    if len(res) > 0:
        db.update_rows(
            'users', [account_type, new_name], ['account_type', 'name'],
            ['id'], [res[0][0]]
        )
        if course_offering is not None:
            enroll_user(res[0][0], course_offering, course_role)
    else:
        db.insert_single(
            'update_account_types',
            [new_name, email, account_type, course_offering],
            ['new_name', 'email', 'account_type', 'course_offering']
        )


def enroll_user(user, course_offering, role):
    res = db.select_columns(
        'enrollments', ['role'],
        ['user', 'course_offering'],
        [user, course_offering]
    )
    if len(res) == 0:
        db.insert_single(
            'enrollments',
            [user, course_offering, role],
            ['user', 'course_offering', 'role']
        )
    else:
        if res[0][0] != role:
            db.update_rows(
                'enrollments', [role], ['role'],
                ['user', 'course_offering'], [user, course_offering]
            )
