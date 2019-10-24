import random
import datetime
import json
import bcrypt

from app.db_manager import sqliteManager as db


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


def gen_sessions():
    ret = []
    for year in range(2000, 2020):
        ret.append(
            'sessions',
            [year, 1, datetime.datetime(year, 1, 1, 0, 0, 0),
                datetime.datetime(year, 4, 30, 23, 59, 59)],
            ['year', 'term', 'start_date', 'end_date']
        )
        ret.append(
            'sessions',
            [year, 2, datetime.datetime(year, 5, 1, 0, 0, 0),
                datetime.datetime(year, 7, 31, 23, 59, 59)],
            ['year', 'term', 'start_date', 'end_date']
        )
        ret.append(
            'sessions',
            [year, 3, datetime.datetime(year, 8, 1, 0, 0, 0),
                datetime.datetime(year, 11, 30, 23, 59, 59)],
            ['year', 'term', 'start_date', 'end_date']
        )
    db.insert_multiple(ret)


def gen_courses():
    with open('db/prereq.json') as f:
        courses = json.load(f)
        query = [('courses', [c['code'], c['name']], ['code', 'name'])
                 for c in courses]
        db.insert_multiple(query)
    with open('db/courses.json') as f:
        courses = json.load(f)
        query = []
        for c in courses:
            db.insert_single('courses',
                             [c['code'], c['name']], ['code', 'name'])
            res = db.select_columns('courses', ['id'],
                                    ['code'], [c['code']])
            assert len(res) > 0
            course_id = res[0][0]

            for year, term, start, end in gen_sessions():
                query.append(('sessions',
                              [year, term, start.timestamp(), end.timestamp()],
                              ['year', 'term', 'start_date', 'end_date']))
        db.insert_multiple(query)


def create_topic(name, description, supervisor, areas):
    res = db.select_columns('users', ['id'], ['name'], [supervisor])
    assert len(res) > 0
    user_id = res[0][0]
    db.insert_single('topics', [name, user_id, description],
                     ['name', 'supervisor', 'description'])
    topic_id = db.select_columns('topics', ['id'], ['name', 'supervisor'],
                                 [name, user_id])[0][0]
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
        sessions = get_sessions()
        for t in tasks:
            res = db.select_columns('courses', ['id'], ['code'], [t['course']])
            assert len(res) > 0
            course_id = res[0][0]

            res = db.select_columns('marking_methods', ['id'], ['name'],
                                    ['{} submission'.format(t['marking'])])
            assert len(res) > 0
            mark_method_id = res[0][0]

            word_limit = t.get('word-limit', random.randrange(400, 8000))

            for year, term, _, _ in sessions:
                res = db.select_columns('sessions', ['id'],
                                        ['year', 'term'],
                                        [year, term])
                assert len(res) > 0
                session_id = res[0][0]

                due = random.randrange(start.timestamp(), end.timestamp())
                db.insert_single('tasks', [t['name'],
                                           session_id,
                                           due,
                                           t['description'],
                                           mark_method_id,
                                           word_limit],
                                 ['name', 'session', 'deadline',
                                  'description', 'marking_method',
                                  'word_limit'])

                res = db.select_columns('tasks', ['id'], ['name', 'session'],
                                        [t['name'], session_id])
                assert len(res) > 0
                task_id = res[0][0]

                if 'files' not in t:
                    continue

                for ft in t['files']:
                    res = db.select_columns('file_types', ['id'],
                                            ['name'], [ft])
                    assert len(res) > 0
                    ft_id = res[0][0]

                    db.insert_single('submission_types', [ft_id, task_id],
                                     ['file_type', 'task'])


if __name__ == '__main__':
    db.connect()
    for tbl in ['users', 'courses', 'topics', 'topic_areas',
                'tasks', 'sessions', 'submission_types']:
        db.conn.execute(f'DELETE FROM {tbl}')
    db.conn.commit()

    random.seed(42)
    print('Generating users...')
    students, supervisors = gen_users()

    print('Generating courses...')
    gen_courses()

    print('Generating topics...')
    gen_topics(students, supervisors)

    print('Generating tasks...')
    gen_tasks()

    print('Done')
