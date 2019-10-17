DROP TABLE IF EXISTS account_types;
CREATE TABLE account_types(
    id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS allowed_files;
CREATE TABLE allowed_files(
    id        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    task      INTEGER NOT NULL,
    extension TEXT NOT NULL,
    FOREIGN KEY(task) REFERENCES tasks(id)
);


DROP TABLE IF EXISTS announcements;
CREATE TABLE announcements(
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    topic  INTEGER,
    course INTEGER,
    text   TEXT NOT NULL,
    CHECK(topic is NOT NULL or course is NOT NULL),
    FOREIGN KEY(topic) REFERENCES topics(id),
    FOREIGN KEY(course) REFERENCES courses(id)
);


DROP TABLE IF EXISTS course_roles;
CREATE TABLE course_roles(
    id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS courses;
CREATE TABLE courses(
    id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    code       TEXT NOT NULL,
    name       TEXT NOT NULL,
    start_date date,
    end_date   date
);


DROP TABLE IF EXISTS marking_methods;
CREATE TABLE marking_methods(
    id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS marks;
CREATE TABLE marks(
    criteria INTEGER NOT NULL,
    mark     INTEGER,
    student  INTEGER NOT NULL,
    marker   INTEGER NOT NULL,
    PRIMARY KEY(criteria, student, marker),
    FOREIGN KEY(criteria) REFERENCES task_criteria(id),
    FOREIGN KEY(student) REFERENCES user(id),
    FOREIGN KEY(marker) REFERENCES user(id)
);


DROP TABLE IF EXISTS material_attachments;
CREATE TABLE material_attachments(
    id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    material INTEGER NOT NULL,
    name     TEXT NOT NULL,
    path     TEXT NOT NULL,
    FOREIGN KEY(material) REFERENCES materials(id)
);


DROP TABLE IF EXISTS materials;
CREATE TABLE materials(
    id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    course      INTEGER NOT NULL,
    name        TEXT NOT NULL,
    visible     INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY(course) REFERENCES courses(id)
);


DROP TABLE IF EXISTS prerequisites;
CREATE TABLE prerequisites(
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    type   INTEGER NOT NULL,
    mark   integeR,
    topic  INTEGER NOT NULL,
    course INTEGER NOT NULL,
    FOREIGN KEY(topic) REFERENCES topics(id),
    FOREIGN KEY(course) REFERENCES courses(id)
);


DROP TABLE IF EXISTS student_topic;
CREATE TABLE student_topic(
    student  INTEGER NOT NULL,
    topic    INTEGER NOT NULL,
    assessor INTEGER,
    PRIMARY KEY(student, topic),
    FOREIGN KEY(student) REFERENCES user(id),
    FOREIGN KEY(topic) REFERENCES topics(id),
    FOREIGN KEY(assessor) REFERENCES user(id)
);


DROP TABLE IF EXISTS submission_types;
CREATE TABLE submission_types(
    id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS submissions;
CREATE TABLE submissions(
    student INTEGER NOT NULL,
    task    INTEGER NOT NULL,
    name    TEXT NOT NULL,
    path    TEXT,
    text    TEXT,
    date    datetime NOT NULL,
    PRIMARY KEY(student, task),
    FOREIGN KEY(student) REFERENCES user(id),
    FOREIGN KEY(task) REFERENCES tasks(id)
);


DROP TABLE IF EXISTS tasks;
CREATE TABLE tasks(
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name            TEXT NOT NULL,
    course          INTEGER NOT NULL,
    deadline        date NOT NULL,
    description     TEXT,
    size_limit      INTEGER,
    visible         INTEGER NOT NULL,
    marking_method  INTEGER NOT NULL,
    submission_type INTEGER NOT NULL,
    FOREIGN KEY(marking_method) REFERENCES marking_methods(id),
    FOREIGN KEY(submission_type) REFERENCES submission_types(id),
    FOREIGN KEY(course) REFERENCES courses(id)
);


DROP TABLE IF EXISTS task_attachments;
CREATE TABLE task_attachments(
    id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    task INTEGER NOT NULL,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    FOREIGN KEY(task) REFERENCES tasks(id)
);


DROP TABLE IF EXISTS task_criteria;
CREATE TABLE task_criteria(
    id          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    task        INTEGER NOT NULL,
    name        TEXT NOT NULL,
    description TEXT,
    max_mark    INTEGER NOT NULL,
    FOREIGN KEY(task) REFERENCES tasks(id)
);


DROP TABLE IF EXISTS topics;
CREATE TABLE topics(
    id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name       TEXT NOT NULL,
    supervisor INTEGER NOT NULL,
    visible    INTEGER NOT NULL,
    FOREIGN KEY(supervisor) REFERENCES user(id)
);


DROP TABLE IF EXISTS topic_areas;
CREATE TABLE topic_areas(
    id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    topic INTEGER NOT NULL,
    name  TEXT NOT NULL,
    FOREIGN KEY(topic) REFERENCES topics(id)
);


DROP TABLE IF EXISTS users;
CREATE TABLE users(
    id           INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    email        TEXT NOT NULL,
    password     TEXT NOT NULL,
    account_type INTEGER NOT NULL,
    FOREIGN KEY(account_type) REFERENCES account_types(id)
);


DROP TABLE IF EXISTS user_course;
CREATE TABLE user_course(
    student INTEGER NOT NULL,
    course  INTEGER NOT NULL,
    role    INTEGER NOT NULL,
    FOREIGN KEY(student) REFERENCES users(id),
    FOREIGN KEY(course) REFERENCES courses(id),
    FOREIGN KEY(role) REFERENCES course_roles(id)
);
