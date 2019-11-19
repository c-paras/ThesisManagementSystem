import random
import datetime
import json
import math
import uuid
import bcrypt

from shutil import copyfile
from shutil import rmtree
from pathlib import Path

from app.db_manager import sqliteManager as db
from app.queries import queries as db_queries

import config


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


def get_all_submission_types():
    types = {}
    res = db.select_columns('submission_methods', ['name', 'id'])
    for name, iden in res:
        types[name] = iden
    return types


def get_all_marking_types():
    types = {}
    res = db.select_columns('marking_methods', ['name', 'id'])
    for name, iden in res:
        types[name] = iden
    return types


def get_all_file_types():
    types = {}
    res = db.select_columns('file_types', ['name', 'id'])
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
                           password, types['student'], '', '', timestamp],
                          ['name', 'email', 'password',
                           'account_type', 'confirm_code',
                           'reset_code', 'date_created']))

        # public users
        public = []
        for i in range(20):
            zid = 'z{}'.format(str(4000001 + i))
            public.append(zid)
            name = names[100+i]['name']
            query.append(('users',
                          [name, f'{zid}@unsw.edu.au',
                           password, types['public'], '', '', timestamp],
                          ['name', 'email', 'password',
                           'account_type', 'confirm_code',
                           'reset_code', 'date_created']))

        # supervisor/assessor users
        supervisors = []
        for i in range(10):
            zid = 'z{}'.format(str(8000001 + i))
            supervisors.append(zid)
            name = names[200+i]['name']
            query.append(('users',
                          [name, f'{zid}@unsw.edu.au',
                           password, types['supervisor'], '', '', timestamp],
                          ['name', 'email', 'password',
                           'account_type', 'confirm_code',
                           'reset_code', 'date_created']))

        # course admin users
        course_admin = []
        for i in range(5):
            zid = 'z{}'.format(str(9000001 + i))
            course_admin.append(zid)
            name = names[300+i]['name']
            query.append(('users',
                          [name, f'{zid}@unsw.edu.au',
                           password, types['course_admin'], '', '', timestamp],
                          ['name', 'email', 'password',
                           'account_type', 'confirm_code',
                           'reset_code', 'date_created']))

        db.insert_multiple(query)


def gen_sessions():
    ret = []

    for year in range(2018, 2019):
        ret.append([year, 1,
                    datetime.datetime(year, 1, 1, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 6, 30, 23, 59, 59).timestamp()
                    ])
        ret.append([year, 2,
                    datetime.datetime(year, 7, 1, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 11, 30, 23, 59, 59).timestamp()
                    ])

    for year in range(2019, 2025):
        ret.append([year, 1,
                    datetime.datetime(year, 2, 18, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 5, 18, 23, 59, 59).timestamp()
                    ])
        ret.append([year, 2,
                    datetime.datetime(year, 6, 3, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 8, 31, 23, 59, 59).timestamp()
                    ])
        ret.append([year, 3,
                    datetime.datetime(year, 9, 16, 0, 0, 0).timestamp(),
                    datetime.datetime(year, 12, 14, 23, 59, 59).timestamp()
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
                session_ids = db_queries.get_session_ids_in_range(2019, 2021)
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


def gen_topic_prereqs(topic_id, course_ids):
    if not random.randrange(0, 15):
        # skip a couple of topics so they don't have prereqs
        return
    course_ids = random.sample(course_ids, random.randrange(1, 4))
    for course_id in course_ids:
        db.insert_single(
            'prerequisites',
            [0, topic_id, course_id],
            ['type', 'topic', 'course']
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

        # remove any topics with empty areas or descriptions
        for i in range(len(topics)-1, -1, -1):
            if len(topics[i]['areas']) == 0:
                topics.pop(i)
            elif len(topics[i]['description']) == 0:
                topics.pop(i)

        topics_per_sup = math.floor(len(topics)/len(supervisors))
        topics_per_sup = min(topics_per_sup, 10)

        course_ids = db.select_columns('courses', ['id'], ['prereq'], [1])
        course_ids = list(map(lambda x: x[0], course_ids))
        base_topic_id = 1
        for sup in supervisors:
            for i in range(0, topics_per_sup):
                t = topics[i+base_topic_id]
                query.append((
                    'topics', [i+base_topic_id, t['name'], sup[0],
                               t['description'], random.randrange(0, 2)],
                    ['id', 'name', 'supervisor', 'description', 'visible']
                ))
                gen_topic_areas(i+base_topic_id, t['areas'])
                gen_topic_prereqs(i+base_topic_id, course_ids)
            base_topic_id += topics_per_sup
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

            res = db.select_columns('submission_methods', ['id'],
                                    ['name'],
                                    ['{} submission'.format(t['submission'])])
            sub_method_id = res[0][0]

            word_limit = t.get('word-limit', random.randrange(400, 5000))

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


def gen_tasks2():
    res = db.select_columns('course_offerings', ['*'])
    marking_methods = get_all_marking_types()
    submission_methods = get_all_submission_types()
    file_types = get_all_file_types()
    task_id = 1

    for co in res:
        course = db.select_columns(
            'courses', ['code', 'name'], ['id'], [co[1]]
        )[0]
        session = db.select_columns(
            'sessions', ['start_date', 'end_date'], ['id'], [co[2]]
        )[0]
        start_date = datetime.datetime.fromtimestamp(session[0])
        end_date = datetime.datetime.fromtimestamp(session[1])
        task_name = ""
        if "thesis a" in course[1].lower() or "part a" in course[1].lower():
            task_name = "Thesis Abstract"
            description = "Present your initial idea"
            word_limit = 1000
            marking_method = marking_methods['requires approval']
            submission_method = submission_methods['text submission']

            dif = datetime.timedelta(days=(7*2), minutes=-1)
            deadline = datetime.datetime.timestamp(start_date + dif)
            db.insert_single(
                'tasks',
                [task_id, task_name, deadline, description, marking_method,
                    word_limit, co[0], submission_method],
                ['id', 'name', 'deadline', 'description', 'marking_method',
                    'word_limit', 'course_offering', 'submission_method']
            )
            task_id += 1

        task_name = course[1] + " Presentation"
        description = "Please present your progress for the current course"
        size_limit = 5
        marking_method = marking_methods['requires mark']
        submission_method = submission_methods['file submission']
        files = [file_types['.pdf']]
        dif = datetime.timedelta(days=(7*8), minutes=-1)
        deadline = datetime.datetime.timestamp(start_date + dif)

        db.insert_single(
            'tasks',
            [task_id, task_name, deadline, description, marking_method,
                size_limit, co[0], submission_method],
            ['id', 'name', 'deadline', 'description', 'marking_method',
                'size_limit', 'course_offering', 'submission_method']
        )
        insert_files(files, task_id)
        task_id += 1

        task_name = course[1] + " Report"
        description = """Please write up a report to cover all of your progress
            made in""" + course[1]
        size_limit = 10
        dif = datetime.timedelta(days=(7*11), minutes=-1)
        deadline = datetime.datetime.timestamp(start_date + dif)
        db.insert_single(
            'tasks',
            [task_id, task_name, deadline, description, marking_method,
                size_limit, co[0], submission_method],
            ['id', 'name', 'deadline', 'description', 'marking_method',
                'size_limit', 'course_offering', 'submission_method']
        )
        insert_files(files, task_id)
        task_id += 1


def insert_files(files, task_id):
    file_types = get_all_file_types()
    for file in files:
        file_id = file
        if file in file_types:
            file_id = file_types[file]
        db.insert_single('submission_types', [file_id, task_id])


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
        if i < int(len(students)/2):
            sessions = all_years[1]  # 2019
            courses = courses_tri
        # uncomment to generate 2020 students
        # elif i < 3*int(len(students)/4):
        #     sessions = all_years[2]  # 2020
        #     courses = courses_tri
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
    sup_ids = db.select_columns(
        'users', ['id'], ['account_type'], [types['supervisor']]
    )

    #
    # Add students supervisor_0 is supervising
    #

    # get possible topics
    topics = db.select_columns('topics', ['id', 'supervisor'],)

    # get all students
    students = db.select_columns('users',
                                 ['id'],
                                 ['account_type'],
                                 [types['student']])

    student_ids = []
    request_student_ids = []
    for student in students:
        number = random.randrange(10)
        if number > 2:
            student_ids.append(student[0])
        else:
            request_student_ids.append(student[0])

    gen_topic_requests(request_student_ids)
    # enroll current and past students students
    # tot_curr_stu = 3
    # student_ids = list(range(0, tot_curr_stu))
    # student_ids.extend(list(range(int(len(students)/2),
    #                               int(len(students)/2+tot_curr_stu))))

    for student_id in student_ids:
        if len(sup_ids) < 2:
            break
        number = random.randrange(len(topics))
        topic = topics[number][0]
        supervisor_id = topics[number][1]
        number = random.randrange(len(sup_ids))
        assessor_id = sup_ids[number][0]
        while assessor_id == supervisor_id:
            number = random.randrange(len(sup_ids))
            assessor_id = sup_ids[number][0]
        db.insert_single('student_topic',
                         [student_id,
                          topic,
                          assessor_id],
                         ['student', 'topic', 'assessor'])


def gen_topic_requests(student_ids):
    #
    # Add students supervisor_0 is being requested by
    #
    request_statuses = get_all_request_types()
    pending_id = request_statuses['pending']
    # get possible topics
    topics = db.select_columns('topics', ['id'])

    for i in student_ids:
        topic_id = random.randrange(len(topics))
        db.insert_single('topic_requests',
                         [i, topics[topic_id][0],
                          pending_id, datetime.datetime.now().timestamp(),
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
    upload_dir = Path(config.STATIC_PATH) / Path(config.FILE_UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    sample_material = Path('db/sample_material.pdf')
    for material in materials:
        stem = Path(str(uuid.uuid4()) + 'sample_material.pdf')
        path = upload_dir / stem
        copyfile(sample_material, path)

        db.insert_single(
            'material_attachments',
            [material[0], str(stem)],
            ['material', 'path']
        )


def gen_task_critera():
    tasks = db.select_columns('tasks', ['id', 'name', 'marking_method'])

    for task in tasks:
        queries = []

        if(task[2] == 1):
            queries.append((
                'task_criteria',
                [task[0], 'Approval', 100],
                ['task', 'name', 'max_mark']
            ))
        else:
            queries.append((
                'task_criteria',
                [task[0], 'Technical Quality and Completeness', 80],
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
    request_types = get_all_request_types()

    for student in students:
        markers = db_queries.get_user_ass_sup(student[0])
        if len(markers) == 0:
            continue
        markers = markers[0]
        if None in markers:
            continue
        tasks = db_queries.get_user_tasks(student[0])
        for task in tasks:
            if 'approval' in task[3]:
                continue
            now = datetime.datetime.now().timestamp()
            deadline = task[4]
            if deadline > now:
                continue
            criteria_ids = db.select_columns(
                'task_criteria', ['id', 'max_mark'], ['task'], [task[0]]
            )
            queries = []

            # create the marks
            for criteria in criteria_ids:
                mark = random.randrange(criteria[1])
                feedback = "smile face"
                queries.append((
                    'marks',
                    [criteria[0], mark, student[0],
                     markers[0], feedback, None]
                ))
                queries.append((
                    'marks',
                    [criteria[0], mark, student[0],
                     markers[1], feedback, None]
                ))

            db.insert_multiple(queries)

            # update status to marked
            db.update_rows('submissions',
                           [request_types['marked']], ['status'],
                           ['student', 'task'], [student[0], task[0]])


def gen_submissions():
    acc_types = get_all_account_types()
    request_types = get_all_request_types()
    students = db.select_columns(
        'users', ['id'], ['account_type'], [acc_types['student']]
    )

    upload_dir = Path(config.STATIC_PATH) / Path(config.FILE_UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    sample_submission = Path('db/sample_submission.pdf')
    for student in students:
        tasks = db_queries.get_user_tasks(student[0])
        now = datetime.datetime.now().timestamp()
        queries = []
        for task in tasks:
            # if task is in the future, don't create a submission
            if task[4] > now:
                deadline_time = datetime.datetime.fromtimestamp(task[4])
                now_time = datetime.datetime.fromtimestamp(now)
                dif = deadline_time - now_time
                if dif.days > 14:
                    continue
                number = random.randrange(10)
                if number > 2:
                    continue
            stem = Path(str(uuid.uuid4()) + 'sample_submission.pdf')
            path = upload_dir / stem
            copyfile(sample_submission, path)
            if 'approval' in task[3]:
                queries.append((
                    'submissions',
                    [student[0], task[0], 'ExCiTiNg Title',
                     None, 'Here is a lengthy essay', now,
                     request_types['approved']]
                ))
            else:
                queries.append((
                    'submissions',
                    [student[0], task[0], 'Normal Title',
                     str(stem), 'Here is a lengthy description', now,
                     request_types['pending mark']]
                ))
        db.insert_multiple(queries)


def gen_task_outline():
    tasks = db.select_columns('tasks', ['id'], None, None)
    upload_dir = Path(config.STATIC_PATH) / Path(config.FILE_UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    sample_attachment = Path('db/sample_attachment.pdf')
    for task in tasks:
        stem = Path(str(uuid.uuid4()) + 'sample_attachment.pdf')
        path = upload_dir / stem
        copyfile(sample_attachment, path)
        db.insert_single(
            'task_attachments',
            [task[0], str(stem)],
            ['task', 'path']
        )


if __name__ == '__main__':
    upload_dir = Path(config.STATIC_PATH) / Path(config.FILE_UPLOAD_DIR)
    if upload_dir.exists():
        rmtree(upload_dir)
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
    gen_tasks2()

    print('Generating enrollments...')
    gen_enrollments()

    print('Generating student topics and topic requests...')
    gen_student_topics()

    print('Generating materials...')
    gen_materials()

    print('Generating material attachments...')
    gen_material_attachments()

    print('Generating task critera...')
    gen_task_critera()

    print("Generating submissions...")
    gen_submissions()

    print('Generating marks...')
    gen_marks()

    print("Generating task attachments...")
    gen_task_outline()

    db.close()
    print('Done')
