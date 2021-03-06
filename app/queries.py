from app.db_manager import sqliteManager as db


class queries:
    def get_course_sessions(course_code):
        res = db.custom_query("""SELECT sessions.year, sessions.term
        FROM courses
        INNER JOIN course_offerings AS co
            ON co.course = courses.id
        INNER JOIN sessions
            ON sessions.id = co.session
        WHERE courses.code = ?""", [course_code])
        return [(r[0], r[1]) for r in res]

    def get_session_ids_in_range(start, end):
        res = db.custom_query("""SELECT id
                                 FROM sessions
                                 WHERE year >= ? AND year < ?""",
                              [start, end])
        return res

    def get_terms_per_year(year):
        res = db.custom_query("""
                                 SELECT DISTINCT(term)
                                 FROM sessions
                                 WHERE year = ?""", [year])
        return len(res)

    def get_year_range():
        res = db.custom_query("SELECT DISTINCT(year) FROM sessions")
        years = [r[0] for r in res]
        return (min(years), max(years))

    def get_tasks_accepted_files(topic_id):
        res = db.custom_query("""
                                 SELECT file_types.name FROM file_types
                                 INNER JOIN submission_types st
                                     ON st.file_type = file_types.id
                                 WHERE st.task = ?
                                 """, [topic_id])
        return [r[0] for r in res]

    def respond_topic(student_id, topic_id, status, timestamp):
        db.custom_query("""UPDATE topic_requests
                           SET status = (SELECT id
                                         FROM request_statuses WHERE name = ?),
                               date_responded = ?
                           WHERE student = ? AND topic = ?""",
                        [status, timestamp, student_id, topic_id])

    def lookup_topic_request(student_id, topic_id):
        res = db.custom_query("""
                                 SELECT users.name, users.email,
                                 topics.name, tq.date_created,
                                 request_statuses.name
                                 FROM topic_requests tq
                                 INNER JOIN topics
                                     ON topics.id = tq.topic
                                 INNER JOIN users
                                     ON tq.student = users.id
                                 INNER JOIN request_statuses
                                     ON tq.status = request_statuses.id
                                 WHERE tq.student = ? AND tq.topic = ?
                              """, [student_id, topic_id])
        return [{'userName': r[0],
                 'email': r[1],
                 'topicName': r[2],
                 'reqDate': r[3],
                 'reqStatus': r[4]} for r in res]

    def get_users_of_type(acc_type):
        res = db.custom_query("""
                                 SELECT users.id, users.name, email FROM users
                                 INNER JOIN account_types
                                     ON users.account_type = account_types.id
                                 WHERE account_types.name = ?
                              """, [acc_type])
        return [{'id': r[0],
                 'name': r[1],
                 'email': r[2]} for r in res]

    # gets the current requests for a given supervisor's email
    def get_curr_topic_requests(email):
        res = db.custom_query("""
                                SELECT stu.id, t.id,
                                       stu.name, stu.email, t.name,
                                       tr.date_created
                                FROM users stu
                                INNER JOIN topic_requests tr
                                    ON stu.id = tr.student
                                INNER JOIN topics t
                                    ON t.id = tr.topic
                                INNER JOIN users sup
                                    ON t.supervisor = sup.id
                                INNER JOIN request_statuses rs
                                    ON tr.status = rs.id
                                WHERE sup.email = ?
                                    AND rs.name = "pending";
                             """, [email])
        return res

    # gets the current requests for a given supervisor's email
    def get_current_super_students(email):
        res = db.custom_query("""
                                SELECT stu.name, stu.email, t.name, stu.id,
                                       MAX(sess.end_date)
                                FROM users stu
                                INNER JOIN student_topic st
                                    ON st.student = stu.id
                                INNER JOIN topics t
                                    ON t.id = st.topic
                                INNER JOIN users sup
                                    ON sup.id = t.supervisor
                                INNER JOIN enrollments en
                                    ON en.user = stu.id
                                INNER JOIN course_offerings co
                                    ON co.id = en.course_offering
                                INNER JOIN sessions sess
                                    ON sess.id = co.session
                                WHERE sup.email = "{my_email}"
                                GROUP BY stu.id;
                             """.format(my_email=email))
        return res

    # gets the current requests for a given supervisor's email
    def get_current_assess_students(email):
        res = db.custom_query("""
                                SELECT stu.name, stu.email, t.name, stu.id,
                                       MAX(sess.end_date)
                                FROM users stu
                                INNER JOIN student_topic st
                                    ON st.student = stu.id
                                INNER JOIN topics t
                                    ON t.id = st.topic
                                INNER JOIN users sup
                                    ON sup.id = st.assessor
                                INNER JOIN enrollments en
                                    ON en.user = stu.id
                                INNER JOIN course_offerings co
                                    ON co.id = en.course_offering
                                INNER JOIN sessions sess
                                    ON sess.id = co.session
                                WHERE sup.email = "{my_email}"
                                GROUP BY stu.id;
                             """.format(my_email=email))
        return res

    # seares the topic_area table for an area, and returns a list of the topic
    # IDs and area names
    def search_topic_areas(area):
        res = db.custom_query("""
                                SELECT ta.name, t.id
                                FROM topics t
                                INNER JOIN topic_to_area tta
                                    ON tta.topic = t.id
                                INNER JOIN topic_areas ta
                                    ON tta.topic_area = ta.id
                                WHERE ta.name = "{topic_area}";
                             """.format(topic_area=area))

        return res

    # gets the names of areas related to a topic id
    def get_topic_areas(topic_id):
        res = db.custom_query("""
                                SELECT ta.name
                                FROM topics t
                                INNER JOIN topic_to_area tta
                                    ON tta.topic = t.id
                                INNER JOIN topic_areas ta
                                    ON tta.topic_area = ta.id
                                WHERE t.id = "{id}";
                             """.format(id=topic_id))

        return res

    # gets the prerequisite codes by topic id
    def get_prereqs_by_topic(topic_id):
        res = db.custom_query(
            """
                SELECT c.code
                FROM courses c
                INNER JOIN prerequisites p
                    ON c.id = p.course
                INNER JOIN topics t
                    ON p.topic = t.id
                WHERE t.id = "{topic_id}"
            """.format(topic_id=topic_id)
        )
        return res

    def get_user_materials(user_id):
        res = db.custom_query(
            """
                SELECT m.id, m.name, s.start_date, s.end_date, c.name
                FROM users u
                INNER JOIN enrollments e
                    ON e.user = u.id
                INNER JOIN course_offerings co
                    ON co.id = e.course_offering
                INNER JOIN sessions s
                    ON s.id = co.session
                INNER JOIN materials m
                    on m.course_offering = co.id
                INNER JOIN courses c
                    on c.id = co.course
                WHERE u.id = "{id}" AND
                    m.visible = 1;
            """.format(id=user_id)
        )
        return res

    def get_user_ass_sup(user_id):
        res = db.custom_query(
            """
                SELECT st.assessor, t.supervisor
                FROM users u
                INNER JOIN student_topic st
                    ON st.student = u.id
                INNER JOIN topics t
                    ON t.id = st.topic
                WHERE u.id = "{id}";
            """.format(id=user_id)
        )
        return res

    def get_user_tasks(user_id):
        res = db.custom_query(
            """
                SELECT
                t.id, t.name, c.name, mm.name, t.deadline
                FROM users u
                INNER JOIN enrollments e
                    ON e.user = u.id
                INNER JOIN course_offerings co
                    ON co.id = e.course_offering
                INNER JOIN courses c
                    ON c.id = co.course
                INNER JOIN tasks t
                    ON t.course_offering = co.id
                INNER JOIN marking_methods mm
                    ON mm.id = t.marking_method
                WHERE u.id = "{id}"
                    AND t.visible = "1";
            """.format(id=user_id)
        )
        return res

    def get_staff_curr_topics(email):
        res = db.custom_query(
            """
                SELECT
                t.name, ta.name, t.visible, t.id
                FROM users u
                INNER JOIN topics t
                    ON u.id = t.supervisor
                INNER JOIN topic_to_area tta
                    ON t.id = tta.topic
                INNER JOIN topic_areas ta
                    ON tta.topic_area = ta.id
                WHERE u.email = "{email}"
            """.format(email=email)
        )
        return res

    def get_general_task_info(task_id):
        res = db.custom_query(
            """
                SELECT c.name, t.name, t.deadline, t.description,
                       sm.name, mm.name, t.size_limit,
                       t.word_limit
                FROM tasks t
                INNER JOIN course_offerings co
                    ON t.course_offering = co.id
                INNER JOIN courses c
                    ON co.course = c.id
                INNER JOIN marking_methods mm
                    ON t.marking_method = mm.id
                INNER JOIN submission_methods sm
                    ON t.submission_method = sm.id
                WHERE t.id = "{id}";
            """.format(id=task_id)
        )
        return res

    def get_task_criteria(task_id):
        res = db.custom_query(
            """
                SELECT tc.name, tc.max_mark
                FROM tasks t
                INNER JOIN task_criteria tc
                    ON tc.task = t.id
                WHERE t.id = "{id}";
            """.format(id=task_id)
        )
        return res

    def get_students_supervisor(student_id):
        res = db.custom_query(
            """
                SELECT staff.id, staff.name
                FROM users stu
                JOIN student_topic st
                    ON stu.id = st.student
                JOIN topics t
                    ON st.topic =t.id
                JOIN users staff
                    ON t.supervisor = staff.id
                WHERE stu.id = "{id}";
            """.format(id=student_id)
        )
        return res

    def get_students_assessor(student_id):
        res = db.custom_query(
            """
                SELECT staff.id, staff.name
                FROM users stu
                JOIN student_topic topic
                    ON stu.id = topic.student
                JOIN users staff
                    ON topic.assessor = staff.id
                WHERE stu.id = "{id}";
            """.format(id=student_id)
        )
        return res

    def get_marks_table(student_id, staff_id, task_id):
        res = db.custom_query(
            """
                SELECT tc.name, m.mark, tc.max_mark, m.feedback
                FROM users stu
                INNER JOIN marks m
                    ON stu.id = m.student
                INNER JOIN users staff
                    ON m.marker = staff.id
                INNER JOIN task_criteria tc
                    ON m.criteria = tc.id
                INNER JOIN tasks t
                    ON t.id = tc.task
                WHERE stu.id = "{student_id}"
                    AND staff.id = "{staff_id}"
                    AND tc.task = "{task_id}";
            """.format(student_id=student_id,
                       staff_id=staff_id,
                       task_id=task_id)
        )
        return res

    def get_submission_status(student_id, task_id):
        res = db.custom_query(
            """
                SELECT rs.name
                FROM submissions
                INNER JOIN request_statuses rs
                    ON rs.id = status
                WHERE student = "{student_id}"
                    AND task = "{task_id}";
            """.format(student_id=student_id,
                       task_id=task_id)
        )
        return res

    def get_material_and_attachment(task_id):
        res = db.custom_query(
            """
                SELECT ta.path
                FROM tasks t
                INNER JOIN task_attachments ta
                    ON ta.task = t.id
                WHERE t.id = "{task_id}";
            """.format(task_id=task_id))
        return res

    def get_student_submissions(student_id):
        res = db.custom_query(
            """
                SELECT
                t.id, t.name, mm.name, s.path, s.date_modified
                FROM users u
                INNER JOIN submissions s
                    ON  s.student = u.id
                INNER JOIN tasks t
                    ON t.id = s.task
                INNER JOIN marking_methods mm
                    ON t.marking_method = mm.id
                WHERE u.id = "{student_id}";
            """.format(student_id=student_id)
        )
        return res

    def get_course_offering_details():
        res = db.custom_query(
            """
                SELECT co.id, c.code, s.term, s.year, c.id, s.id, c.name
                FROM course_offerings co
                INNER JOIN sessions s
                    ON s.id = co.session
                INNER JOIN courses c
                    on c.id = co.course
            """
        )
        return res

    def get_student_enrollments(co_id):
        res = db.custom_query(
            """
                SELECT u.id, u.name, u.email, t.name
                FROM users u
                INNER JOIN enrollments e
                    ON e.user = u.id
                LEFT JOIN student_topic st
                    ON st.student = u.id
                LEFT JOIN topics t
                    ON t.id = st.topic
                WHERE e.course_offering = "{co_id}";
            """.format(co_id=co_id)
        )
        return res

    def get_allowed_task_attachments(user_id):
        res = db.custom_query('''
            SELECT path
            FROM task_attachments
            WHERE task IN (
                SELECT id
                FROM tasks
                WHERE visible = 1
                AND course_offering IN (
                    SELECT course_offering
                    FROM enrollments
                    WHERE user = {user_id}
                )
            );'''.format(user_id=user_id)
        )
        return list(map(lambda x: x[0], res))

    def get_allowed_material_attachments(user_id):
        res = db.custom_query('''
            SELECT path
            FROM material_attachments
            WHERE material IN (
                SELECT id
                FROM materials
                WHERE visible = 1
                AND course_offering IN (
                    SELECT course_offering
                    FROM enrollments
                    WHERE user = {user_id}
                )
            );'''.format(user_id=user_id)
        )
        return list(map(lambda x: x[0], res))

    def get_past_task_data(task_id):
        res = db.custom_query('''
            SELECT t.name, t.deadline, t.description, sm.name, t.word_limit,
                   t.size_limit, ft.name, mm.name
            FROM tasks t
            INNER JOIN submission_methods sm
                ON sm.id = t.submission_method
            INNER JOIN marking_methods mm
                ON mm.id = t.marking_method
            LEFT JOIN submission_types st
                ON t.id = st.task
            LEFT JOIN file_types ft
                ON st.file_type = ft.id
            WHERE t.id={task_id}
            ;'''.format(task_id=task_id)
        )
        return res

    def get_student_topic(student_id):
        res = db.custom_query('''
            SELECT name
            FROM topics
            WHERE id = (
                SELECT topic
                FROM student_topic
                WHERE student = {student_id}
            )
            ;'''.format(student_id=student_id)
        )
        return res

    def is_fully_marked(student_id, task_id):
        res = db.custom_query('''
            SELECT COUNT(m.student) == (SELECT COUNT(DISTINCT tc.id)*2
                            FROM tasks t
                            INNER JOIN task_criteria tc
                                ON tc.task = t.id
                            WHERE t.id = {task_id})
            FROM tasks t
            INNER JOIN submissions s
                ON t.id = s.task
            INNER JOIN task_criteria tc
                ON tc.task = t.id
            INNER JOIN marks m
                ON tc.id = m.criteria
                AND s.student = m.student
            WHERE t.id = {task_id}
                AND s.student = {student_id}
            ;'''.format(student_id=student_id, task_id=task_id)
        )
        return res[0][0]

    def is_partially_marked(student_id, task_id):
        res = db.custom_query('''
            SELECT COUNT(m.student) > 0
            FROM tasks t
            INNER JOIN submissions s
                ON t.id = s.task
            INNER JOIN task_criteria tc
                ON tc.task = t.id
            INNER JOIN marks m
                ON tc.id = m.criteria
                AND s.student = m.student
            WHERE t.id = {task_id}
                AND s.student = {student_id}
            ;'''.format(student_id=student_id, task_id=task_id)
        )
        return res[0][0]
