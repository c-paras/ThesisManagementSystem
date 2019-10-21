from app.db_manager import sqliteManager as db
import bcrypt
import random


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
        zid = str(1000000 + i)
        students.append(zid)
        query.append(('users',
                      [zid, zid + '@unsw.edu.au',
                       password, types['student']],
                      ['name', 'email', 'password', 'account_type']))

    supervisors = []
    for i in range(1, 10):
        zid = str(8000000 + i)
        supervisors.append(zid)
        query.append(('users',
                      [zid, zid + '@unsw.edu.au',
                       password, types['supervisor']],
                      ['name', 'email', 'password', 'account_type']))
    db.insert_multiple(query)
    return (students, supervisors)


def gen_courses():
    courses = [('COMP3121', 'Algorithms and Programming Techniques'),
               ('COMP3131', 'Programming Languages and Compilers'),
               ('COMP3141', 'Software System Design and Implementation'),
               ('COMP3151', 'Foundations of Concurrency'),
               ('COMP3153', 'Algorithmic Verification'),
               ('COMP3161', 'Concepts of Programming Languages'),
               ('COMP3211', 'Computer Architecture'),
               ('COMP3222', 'Digital Circuits and Systems'),
               ('COMP3231', 'Operating Systems'),
               ('COMP3311', 'Database Systems'),
               ('COMP3331', 'Computer Networks and Applications'),
               ('COMP3411', 'Artificial Intelligence'),
               ('COMP3421', 'Computer Graphics'),
               ('COMP3431', 'Robotic Software Architecture'),
               ('COMP3511', 'Human Computer Interaction'),
               ('COMP3601', 'Design Project A'),
               ('COMP3821', 'Extended Algorithms and Programming Techniques'),
               ('COMP3891', 'Extended Operating Systems'),
               ('COMP3900', 'Computer Science Project'),
               ('COMP3901', 'Special Project A'),
               ('COMP3902', 'Special Project B'),
               ('COMP4121', 'Advanced and Parallel Algorithms'),
               ('COMP4128', 'Programming Challenges'),
               ('COMP4141', 'Theory of Computation'),
               ('COMP4161', 'Advanced Topics in Software Verification'),
               ('COMP4336', 'Mobile Data Networking'),
               ('COMP4337', 'Securing Wireless Networks'),
               ('COMP4418', 'Knowledge Representation and Reasoning'),
               ('COMP4511', 'User Interface Design and Construction'),
               ('COMP4601', 'Design Project B'),
               ('COMP4920', 'Management and Ethics'),
               ('COMP4930', 'Thesis Part A'),
               ('COMP4931', 'Thesis Part B'),
               ('COMP4941', 'Thesis Part B'),
               ('COMP4951', 'Research Thesis A'),
               ('COMP4952', 'Research Thesis B'),
               ('COMP4953', 'Research Thesis C'),
               ('COMP4961', 'Computer Science Thesis A'),
               ('COMP4962', 'Computer Science Thesis B'),
               ('COMP4963', 'Computer Science Thesis C'),
               ('COMP6324',
                'Internet of Things Service Design and Engineering'),
               ('COMP6441', 'Security Engineering and Cyber Security'),
               ('COMP6443', 'Web Application Security and Testing'),
               ('COMP6445', 'Digital Forensics'),
               ('COMP6447', 'System and Software Security Assessment'),
               ('COMP6448', 'Security Engineering Masterclass'),
               ('COMP6451',
                'Cryptocurrency and Distributed Ledger Technologies'),
               ('COMP6452',
                'Software Architecture for Blockchain Applications'),
               ('COMP6714', 'Information Retrieval and Web Search'),
               ('COMP6721', '(In-)Formal Methods: The Lost Art'),
               ('COMP6733', 'Internet of Things Experimental Design Studio'),
               ('COMP6741', 'Parameterized and Exact Computation'),
               ('COMP6752', 'Modelling Concurrent Systems'),
               ('COMP6771', 'Advanced C++ Programming'),
               ('COMP6841',
                'Extended Security Engineering and Cyber Security'),
               ('COMP6843', 'Extended Web Application Security and Testing'),
               ('COMP6845',
                'Extended Digital Forensics and Incident Response'),
               ('COMP9242', 'Advanced Operating Systems'),
               ('COMP9243', 'Distributed Systems'),
               ('COMP9301', 'Cyber Security Project'),
               ('COMP9302', 'Cyber Security Project B'),
               ('COMP9313', 'Big Data Management'),
               ('COMP9315', 'Database Systems Implementation'),
               ('COMP9318', 'Data Warehousing and Data Mining'),
               ('COMP9319', 'Web Data Compression and Search'),
               ('COMP9321', 'Data Services Engineering'),
               ('COMP9322', 'Software Service Design and Engineering'),
               ('COMP9323', 'Software as a Service Project'),
               ('COMP9332', 'Network Routing and Switching'),
               ('COMP9334',
                'Capacity Planning of Computer Systems and Networks'),
               ('COMP9417', 'Machine Learning and Data Mining'),
               ('COMP9418', 'Advanced Topics in Statistical Machine Learning'),
               ('COMP9444', 'Neural Networks and Deep Learning'),
               ('COMP9517', 'Computer Vision')]
    query = []
    course_codes = []
    for courseid, name in courses:
        course_codes.append(courseid)
        query.append(('courses', [courseid, name], ['code', 'name']))
    db.insert_multiple(query)
    return course_codes


def create_topic(name, supervisor, areas):
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
    db.insert_multiple(query)


def gen_topics(students, supervisors):
    topics = [
        ('3D Visualisation of Robot Sensor Data', ['Graphics', 'Robotics']),
        ('Research and improve the material design language',
         ['User Interfaces']),
        ('Improve the Moodle Page', ['User Interfaces'])]
    random.seed(42)
    for topic, areas in topics:
        supervisor = supervisors[random.randrange(0, len(supervisors))]
        create_topic(topic, supervisor, areas)


if __name__ == '__main__':
    db.connect()
    for tbl in ['users', 'courses', 'topics', 'topic_areas']:
        db.conn.execute(f'DELETE FROM {tbl}')
        db.conn.commit()
    print('Generating users...')
    students, supervisors = gen_users()

    print('Generating courses...')
    courses = gen_courses()

    print('Generating topics...')
    gen_topics(students, supervisors)
