import random
import datetime
import json
import bcrypt

from app.db_manager import sqliteManager as db
from app.queries import queries as db_queries


def get_all_account_types():
    types = {}
    res = db.select_columns('account_types', ['name', 'id'])
    for name, iden in res:
        types[name] = iden
    return types


def get_all_request_types():
    types = {}
    res = db.select_columns('request_statuses', ['name', 'id'])
    for name, iden in res:
        types[name] = iden
    return types


def gen_users():
    with open('db/names.json') as f:
        names = json.load(f)
        types = get_all_account_types()
        password = bcrypt.hashpw('password1'.encode('utf-8'), bcrypt.gensalt())
        query = []
        timestamp = 946645140

        # student users
        students = []
        for i in range(100):
            zid = 'z{}'.format(str(1000001 + i))
            students.append(zid)
            name = names[i]['name']
            query.append(('users',
                          [name, f'{zid}@unsw.edu.au',
                           password, types['student'], '', timestamp],
                          ['name', 'email', 'password',
                           'account_type', 'confirm_code', 'date_created']))

        # public users
        public = []
        for i in range(20):
            zid = 'z{}'.format(str(4000001 + i))
            public.append(zid)
            name = names[100+i]['name']
            query.append(('users',
                          [name, f'{zid}@unsw.edu.au',
                           password, types['public'], '', timestamp],
                          ['name', 'email', 'password',
                           'account_type', 'confirm_code', 'date_created']))

        # supervisor/assessor users
        supervisors = []
        for i in range(10):
            zid = 'z{}'.format(str(8000001 + i))
            supervisors.append(zid)
            name = names[200+i]['name']
            query.append(('users',
                          [name, f'{zid}@unsw.edu.au',
                           password, types['supervisor'], '', timestamp],
                          ['name', 'email', 'password',
                           'account_type', 'confirm_code', 'date_created']))

        # course admin users
        course_admin = []
        for i in range(5):
            zid = 'z{}'.format(str(9000001 + i))
            course_admin.append(zid)
            name = names[300+i]['name']
            query.append(('users',
                          [name, f'{zid}@unsw.edu.au',
                           password, types['course_admin'], '', timestamp],
                          ['name', 'email', 'password',
                           'account_type', 'confirm_code', 'date_created']))

        db.insert_multiple(query)


def gen_sessions():
    ret = []
    for year in range(2000, 2019):
        ret.append([year, 1,
                    datetime.datetime(year, 1, 1, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 6, 30, 23, 59, 59).timestamp()
                    ])
        ret.append([year, 2,
                    datetime.datetime(year, 7, 1, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 11, 30, 23, 59, 59).timestamp()
                    ])

    for year in range(2019, 2021):
        ret.append([year, 1,
                    datetime.datetime(year, 1, 1, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 4, 30, 23, 59, 59).timestamp()
                    ])
        ret.append([year, 2,
                    datetime.datetime(year, 5, 1, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 7, 31, 23, 59, 59).timestamp()
                    ])
        ret.append([year, 3,
                    datetime.datetime(year, 8, 1, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 11, 30, 23, 59, 59).timestamp()
                    ])

    query = []
    for sess in ret:
        query.append(('sessions',
                      sess,
                      ['year', 'term', 'start_date', 'end_date']))
    db.insert_multiple(query)
    return ret


def gen_courses():
    with open('db/prereq.json') as f:
        courses = json.load(f)
        for c in courses:
            db.insert_single('courses',
                             [c['code'], c['name'], 1],
                             ['code', 'name', 'prereq'])
    with open('db/courses.json') as f:
        courses = json.load(f)
        for c in courses:
            db.insert_single('courses',
                             [c['code'], c['name'], 0],
                             ['code', 'name', 'prereq'])


def gen_course_offering():
    with open('db/courses.json') as f:
        query = []
        for c in json.load(f):
            res = db.select_columns('courses', ['id'],
                                    ['code'], [c['code']])
            assert len(res) > 0
            course_id = res[0][0]
            if(c['semester']):
                # create offerings for thesis A/B in years before 2019
                session_ids = db.select_columns_operator('sessions',
                                                         ['id'],
                                                         ['year'],
                                                         ['2019'],
                                                         '<')

                for session_id in session_ids:
                    db.insert_single('course_offerings',
                                     [course_id, session_id[0]],
                                     ['course', 'session'])

            else:
                # create offering for thesis A/B/C in years after 2018
                session_ids = db.select_columns_operator('sessions',
                                                         ['id'],
                                                         ['year'],
                                                         ['2019'],
                                                         '>=')

                for session_id in session_ids:
                    db.insert_single('course_offerings',
                                     [course_id, session_id[0]],
                                     ['course', 'session'])


def gen_topic_areas(topic_id, areas):
    query = []
    for area in areas:
        res = db.select_columns('topic_areas', ['name'], ['name'], [area])
        if len(res) == 0:
            db.insert_single(
                'topic_areas', [area], ['name']
            )
        area_id = db.select_columns(
            'topic_areas', ['id'], ['name'], [area]
        )[0][0]
        db.insert_single(
            'topic_to_area', [topic_id, area_id], ['topic', 'topic_area']
        )


def gen_topics():
    with open('db/topics.json') as f:
        topics = json.load(f)
        query = []

        supervisor_type = db.select_columns('account_types',
                                            ['id'],
                                            ['name'],
                                            ['supervisor'])[0][0]

        supervisors = db.select_columns('users',
                                        ['id'],
                                        ['account_type'],
                                        [supervisor_type])

        topic_id = 1
        for t in topics:
            supervisor = supervisors[random.randrange(0, len(supervisors))][0]
            query.append((
                'topics', [topic_id, t['name'], supervisor, t['description']],
                ['id', 'name', 'supervisor', 'description']
            ))
            gen_topic_areas(topic_id, t['areas'])
            topic_id += 1
        db.insert_multiple(query)


def gen_tasks():
    with open('db/tasks.json') as f:
        tasks = json.load(f)

        for t in tasks:
            res = db.select_columns('courses', ['id'], ['code'], [t['course']])
            assert len(res) > 0
            course_id = res[0][0]

            res = db.select_columns('marking_methods', ['id'], ['name'],
                                    ['requires {}'.format(t['marking'])])
            assert len(res) > 0
            mark_method_id = res[0][0]

            submission_type = db.select_columns(
                'marking_methods',
                ['id'], ['name'], ['{} submission'.format(t['submission'])]
            )

            sub_method_id = res[0][0]

            word_limit = t.get('word-limit', random.randrange(400, 8000))

            offerings = db.select_columns('course_offerings',
                                          ['id', 'session'],
                                          ['course'],
                                          [course_id])

            for offer_id, session_id in offerings:
                date = db.select_columns('sessions',
                                         ['start_date', 'end_date'],
                                         ['id'],
                                         [session_id])

                due = datetime.datetime.fromtimestamp(
                                random.randrange(date[0][0], date[0][1])
                                ).replace(hour=23,
                                          minute=59,
                                          second=59
                                          ).timestamp()

                db.insert_single(
                    'tasks',
                    [t['name'], offer_id, due, t['description'],
                        mark_method_id, word_limit, sub_method_id],
                    ['name', 'course_offering', 'deadline',
                        'description', 'marking_method', 'word_limit',
                        'submission_method']
                )

                res = db.select_columns('tasks', ['id'],
                                        ['name', 'course_offering'],
                                        [t['name'], offer_id])
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


def gen_enrollments():
    types = get_all_account_types()

    # get all sessions in the years (2018, 2019, 2020) and put each year into
    # a list
    all_years = []
    for year in range(2018, 2021):
        res = db.select_columns('sessions',
                                ['id'],
                                ['year'],
                                [year])
        all_years.append(res)

    # get all courses for old semesters
    courses_sem = []
    for code in ['COMP4930', 'COMP4931']:
        courses_sem += db.select_columns('courses',
                                         ['id'],
                                         ['code'],
                                         [code])

    # get all courses for old semesters
    courses_tri = []
    for code in ['COMP4951', 'COMP4952', 'COMP4953']:
        courses_tri += db.select_columns('courses',
                                         ['id'],
                                         ['code'],
                                         [code])

    # get all students
    students = db.select_columns('users',
                                 ['id'],
                                 ['account_type'],
                                 [types['student']])

    # create entries in the enrollments table
    for i, (student, ) in enumerate(students):

        # decide what year current student is enrolled in
        if i < int(len(students)/3):
            sessions = all_years[1]  # 2019
            courses = courses_tri
        elif i < int(len(students)/2):
            sessions = all_years[2]  # 2020
            courses = courses_tri
        else:
            sessions = all_years[0]  # 2018
            courses = courses_sem

        # enroll the student
        for i, (course, ) in enumerate(courses):
            course_offering = db.select_columns('course_offerings',
                                                ['id'],
                                                ['session', 'course'],
                                                [sessions[i][0], course])
            assert len(course_offering) > 0

            course_offering = course_offering[0][0]
            db.insert_single('enrollments',
                             [student, course_offering],
                             ['user', 'course_offering'])


def gen_student_topics():
    types = get_all_account_types()
    # get first supervisor

    main_sup_id = db.select_columns('users',
                                    ['id'],
                                    ['account_type'],
                                    [types['supervisor']])[0][0]

    #
    # Add students supervisor_0 is supervising
    #

    # get possible topics
    topics = db.select_columns('topics',
                               ['id'],
                               ['supervisor'],
                               [main_sup_id])

    # get all students
    students = db.select_columns('users',
                                 ['id'],
                                 ['account_type'],
                                 [types['student']])

    # enroll current and past students students
    tot_curr_stu = 3
    student_ids = list(range(0, tot_curr_stu))
    student_ids.extend(list(range(int(len(students)/2),
                                  int(len(students)/2+tot_curr_stu))))

    for i in student_ids:
        topic_id = random.randrange(0, len(topics))
        db.insert_single('student_topic',
                         [students[i][0], topics[topic_id][0]],
                         ['student', 'topic'])

    #
    # Add students supervisor_0 is assessing
    #

    other_super = db.select_columns('users',
                                    ['id'],
                                    ['account_type'],
                                    [types['supervisor']])[1][0]

    # get possible topics
    topics = db.select_columns('topics',
                               ['id'],
                               ['supervisor'],
                               [other_super])

    # get all students
    students = db.select_columns('users',
                                 ['id'],
                                 ['account_type'],
                                 [types['student']])

    # enroll current and past students students

    student_ids = list(range(tot_curr_stu,
                             2*tot_curr_stu))
    student_ids.extend(list(range(int(len(students)/2+tot_curr_stu),
                                  int(len(students)/2+tot_curr_stu*2))))

    for i in student_ids:
        topic_id = random.randrange(0, len(topics))
        db.insert_single('student_topic',
                         [students[i][0],
                          topics[topic_id][0],
                          main_sup_id],
                         ['student', 'topic', 'assessor'])


def gen_topic_requests():
    types = get_all_account_types()
    # get first supervisor

    main_sup_id = db.select_columns('users',
                                    ['id'],
                                    ['account_type'],
                                    [types['supervisor']])[0][0]

    #
    # Add students supervisor_0 is being requested by
    #

    # get possible topics
    topics = db.select_columns('topics',
                               ['id'],
                               ['supervisor'],
                               [main_sup_id])

    # get all students
    students = db.select_columns('users',
                                 ['id'],
                                 ['account_type'],
                                 [types['student']])

    # enroll current and past students students
    student_ids = list(range(int(len(students)/3),
                             int(len(students)/3+3)))

    for i in student_ids:
        topic_id = random.randrange(0, len(topics))
        db.insert_single('topic_requests',
                         [students[i][0], topics[topic_id][0],
                          1, datetime.datetime.now().timestamp(),
                          'FAKE_GEN_DATA'],
                         ['student', 'topic', 'status',
                          'date_created', 'text'])


def gen_materials():
    course_offerings = db.select_columns('course_offerings', ['id', 'course'])

    # currently adds a presentation and report for each thesis
    for course in course_offerings:

        # filtering out any courses not a thesis
        name = db.select_columns(
            'courses', ['name'], ['id'], [course[1]]
        )
        if len(name) == 0:
            continue
        name = name[0][0].lower()
        if 'thesis' not in name:
            continue
        # entering 2 materials for each thesis
        queries = []
        queries.append((
            'materials',
            ['Course outline', course[0]],
            ['name', 'course_offering']
        ))
        queries.append((
            'materials',
            [f'Sample report {name}', course[0]],
            ['name', 'course_offering']
        ))
        db.insert_multiple(queries)


def gen_material_attachments():
    materials = db.select_columns('materials', ['id'])

    for material in materials:
        path = "img/chicken.jpg"
        db.insert_single(
            'material_attachments',
            [material[0], path],
            ['material', 'path']
        )


def gen_task_critera():
    tasks = db.select_columns('tasks', ['id', 'name'])

    for task in tasks:
        queries = []
        queries.append((
            'task_criteria',
            [task[0], 'Technical Quality and Completeness of the work', 80],
            ['task', 'name', 'max_mark']
        ))
        queries.append((
            'task_criteria',
            [task[0], 'Structure and Presentation', 20],
            ['task', 'name', 'max_mark']
        ))
        db.insert_multiple(queries)


def gen_marks():
    acc_types = get_all_account_types()
    students = db.select_columns(
        'users', ['id'], ['account_type'], [acc_types['student']]
    )

    for student in students:
        markers = db_queries.get_user_ass_sup(student[0])
        if len(markers) == 0:
            continue
        markers = markers[0]
        if None in markers:
            continue
        tasks = db_queries.get_user_tasks(student[0])
        for task in tasks:
            criteria_ids = db.select_columns(
                'task_criteria', ['id', 'max_mark'], ['task'], [task[0]]
            )
            queries = []
            for criteria in criteria_ids:
                mark = random.randrange(criteria[1])
                feedback = "smile face"
                path = "img/chicken.jpg"
                queries.append((
                    'marks',
                    [criteria[0], mark, student[0], markers[0], feedback, path]
                ))
                mark = random.randrange(criteria[1])
                queries.append((
                    'marks',
                    [criteria[0], mark, student[0], markers[1], feedback, path]
                ))
            db.insert_multiple(queries)


def gen_submissions():
    acc_types = get_all_account_types()
    request_types = get_all_request_types()
    students = db.select_columns(
        'users', ['id'], ['account_type'], [acc_types['student']]
    )

    for student in students:
        tasks = db_queries.get_user_tasks(student[0])
        now = datetime.datetime.now().timestamp()
        queries = []
        for task in tasks:
            # if task is in the future, don't create a submission
            if task[4] > now:
                continue
            if 'approval' in task[3]:
                queries.append((
                    'submissions',
                    [student[0], task[0], 'smiley',
                        'img/chicken.jpg', 'ez', now,
                        request_types['approved']]
                ))
            else:
                queries.append((
                    'submissions',
                    [student[0], task[0], 'smiley',
                        'img/chicken.jpg', 'ez', now, request_types['marked']]
                ))
        db.insert_multiple(queries)


if __name__ == '__main__':
    db.connect()

    print('Dropping all existing tables...')
    tables = db.custom_query('''
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%';
    ''')
    for tbl in tables:
        db.delete_all(tbl[0])

    db.init_db()

    random.seed(42)
    print('Generating users...')
    gen_users()

    print('Generating courses...')
    gen_courses()

    print('Generating sessions...')
    gen_sessions()

    print('Generating course offerings...')
    gen_course_offering()

    print('Generating topics...')
    gen_topics()

    print('Generating tasks...')
    gen_tasks()

    print('Generating enrollments...')
    gen_enrollments()

    print('Generating student topics...')
    gen_student_topics()

    print('Generating topic requests...')
    gen_topic_requests()

    print('Generating materials...')
    gen_materials()

    print('Generating material attachments...')
    gen_material_attachments()

    print('Generating task critera...')
    gen_task_critera()

    print('Generating marks...')
    gen_marks()

    print("Generating submissions...")
    gen_submissions()

    db.close()
    print('Done')
