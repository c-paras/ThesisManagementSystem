import csv

from app.db_manager import sqliteManager as db
from app.file_upload import FileUpload


def get_all_account_types():
    types = {}
    res = db.select_columns('account_types', ['name', 'id'])
    for name, iden in res:
        types[name] = iden
    return types

# expects a csv file in format
# email, new_name, account_type


def update_from_file(url, couse_offering=None):
    # TODO use proper upload file if necessary
    with open(url) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        account_types = get_all_account_types()
        for row in csv_file:
            account_type = row[2]
            if row[2] in account_types:
                account_type = account_types[row[2]]

            update_account_type(row[0], row[1], account_type, course_offering)


def update_account_type(email, new_name, account_type, course_offering=None):

    account_types = get_all_account_types()
    course_role = 'staff'
    if account_types['student'] == account_type:
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
    db.insert_single(
        'enrollments',
        [user, course_offering, role],
        ['user', 'course_offering', 'role']
    )
