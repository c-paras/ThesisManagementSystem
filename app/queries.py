from app.db_manager import sqliteManager as db


class queries:

    # gets the current requests for a given supervisor's email
    def get_curr_topic_requests(email):
        res = db.custom_query("""
                                SELECT stu.name, stu.email, t.name
                                FROM users stu
                                INNER JOIN topic_requests tr
                                    ON stu.id = tr.student
                                INNER JOIN topics t
                                    ON t.id = tr.topic
                                INNER JOIN users sup
                                    ON t.supervisor = sup.id
                                INNER JOIN request_statuses rs
                                    ON tr.status = rs.id
                                WHERE sup.email = "{my_email}"
                                    AND rs.name = "pending";
                             """.format(my_email=email))
        return res

    # gets the current requests for a given supervisor's email
    def get_current_super_students(email):
        res = db.custom_query("""
                                SELECT stu.name, stu.email, t.name,
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
                                SELECT stu.name, stu.email, t.name,
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

    def get_user_materials(user_id):
        res = db.custom_query(
            """
                SELECT m.id, m.name, s.start_date, s.end_date
                FROM users u
                INNER JOIN enrollments e
                    ON e.user = u.id
                INNER JOIN course_offerings co
                    ON co.id = e.course_offering
                INNER JOIN sessions s
                    ON s.id = co.session
                INNER JOIN materials m
                    on m.course_offering = co.id
                WHERE u.id = "{id}";
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
                SELECT t.id, t.name, c.name
                FROM users u
                INNER JOIN enrollments e
                    ON e.user = u.id
                INNER JOIN course_offerings co
                    ON co.id = e.course_offering
                INNER JOIN courses c
                    ON c.id = co.course
                INNER JOIN tasks t
                    ON t.course_offering = co.id
                WHERE u.id = "{id}";
            """.format(id=user_id)
        )
        return res
