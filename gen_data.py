from app.db_manager import sqliteManager as db
import bcrypt
import random
import datetime
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


def gen_tasks():
    with open('db/tasks.json') as f:
        tasks = json.load(f)
        for t in tasks:
            dt = '{} {}'.format(t['deadline']['date'], t['deadline']['time'])
            due = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M')

            res = db.select_columns('courses', ['id'], ['code'], [t['course']])
            assert len(res) > 0
            course_id = res[0][0]

            db.insert_single('sessions', [0, 0, course_id],
                             ['start_date', 'end_date', 'course'])
            res = db.select_columns('sessions', ['id'],
                                    ['start_date', 'end_date', 'course'],
                                    [0, 0, course_id])
            assert len(res) > 0
            session_id = res[0][0]

            res = db.select_columns('marking_methods', ['id'], ['name'],
                                    ['{} submission'.format(t['marking'])])
            assert len(res) > 0
            mark_method_id = res[0][0]

            db.insert_single('tasks', [t['name'],
                                       session_id,
                                       due.timestamp(),
                                       t['description'],
                                       mark_method_id],
                             ['name', 'session', 'deadline',
                              'description', 'marking_method'])

            res = db.select_columns('tasks', ['id'], ['name', 'session'],
                                    [t['name'], session_id])
            assert len(res) > 0
            task_id = res[0][0]

            for ft in t['files']:
                res = db.select_columns('file_types', ['id'], ['name'], [ft])
                assert len(res) > 0
                ft_id = res[0][0]

                db.insert_single('submission_types', [ft_id, task_id],
                                 ['file_type', 'task'])


if __name__ == '__main__':
    db.connect()
    for tbl in ['users', 'courses', 'topics', 'topic_areas',
                'tasks', 'submission_types']:
        db.conn.execute(f'DELETE FROM {tbl}')
    db.conn.commit()

    random.seed(42)
    print('Generating users...')
    students, supervisors = gen_users()

    print('Generating courses...')
    courses = gen_courses()

    print('Generating topics...')
    gen_topics(students, supervisors)

    print('Generating tasks...')
    gen_tasks()

    print('Done')
