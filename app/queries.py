from app.db_manager import sqliteManager as db


class queries:

    # gets the current requests for a given supervisor's email
    def get_curr_topic_requests(email):
        db.connect()

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

        db.close()
        return res

    # gets the current requests for a given supervisor's email
    def get_current_super_students(email):
        db.connect()

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

        db.close()
        return res

    # gets the current requests for a given supervisor's email
    def get_current_assess_students(email):
        db.connect()

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

        db.close()
        return res
