from app.db_manager import sqliteManager as db
import bcrypt
import random
import json


def get_all_types():
    types = {}
    res = db.conn.execute('SELECT name, id FROM account_types').fetchall()
    for name, iden in res:
        types[name] = iden
    return types


def gen_users():
    types = get_all_types()
    password = bcrypt.hashpw('password1'.encode('utf-8'), bcrypt.gensalt())
    query = []
    students = []
    for i in range(1, 100):
        zid = 'z{}'.format(str(1000000 + i))
        students.append(zid)
        query.append(('users',
                      [zid, f'{zid}@unsw.edu.au',
                       password, types['student']],
                      ['name', 'email', 'password', 'account_type']))

    supervisors = []
    for i in range(1, 10):
        zid = 'z{}'.format(str(8000000 + i))
        supervisors.append(zid)
        query.append(('users',
                      [zid, f'{zid}@unsw.edu.au',
                       password, types['supervisor']],
                      ['name', 'email', 'password', 'account_type']))
    db.insert_multiple(query)
    return (students, supervisors)


def gen_courses():
    with open('db/courses.json') as f:
        courses = json.load(f)
        query = []
        for c in courses:
            query.append(('courses', [c['code'], c['name']], ['code', 'name']))
            db.insert_multiple(query)


def create_topic(name, description, supervisor, areas):
    user_dbid = db.select_columns('users',
                                  ['id'], ['name'], [supervisor])[0][0]
    db.insert_single('topics', [name, user_dbid,
                                f'{name} is a very interesting topic'],
                     ['name', 'supervisor', 'description'])
    topic_id = db.select_columns('topics', ['id'], ['name', 'supervisor'],
                                 [name, user_dbid])[0][0]
    query = []
    for area in areas:
        query.append(('topic_areas', [area, topic_id], ['name', 'topic']))
    return query


def gen_topics(students, supervisors):
    with open('db/topics.json') as f:
        topics = json.load(f)
        query = []
        for t in topics:
            supervisor = supervisors[random.randrange(0, len(supervisors))]
            query.extend(create_topic(t['name'], t['description'],
                                      supervisor, t['areas']))
        db.insert_multiple(query)


if __name__ == '__main__':
    db.connect()
    for tbl in ['users', 'courses', 'topics', 'topic_areas']:
        db.conn.execute(f'DELETE FROM {tbl}')
        db.conn.commit()
    random.seed(42)
    print('Generating users...')
    students, supervisors = gen_users()

    print('Generating courses...')
    courses = gen_courses()

    print('Generating topics...')
    gen_topics(students, supervisors)
