DROP TABLE IF EXISTS account_types;
CREATE TABLE account_types(
    id          INTEGER NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS allowed_files;
CREATE TABLE allowed_files(
    id        INTEGER NOT NULL PRIMARY KEY,
    task      INTEGER NOT NULL,
    extension TEXT NOT NULL, -- can change to mask --
    FOREIGN KEY(task) REFERENCES tasks(id)
);


DROP TABLE IF EXISTS announcements;
CREATE TABLE announcements(
    id              INTEGER NOT NULL PRIMARY KEY,
    topic           INTEGER,
    course_offering INTEGER,
    text            TEXT NOT NULL,
    CHECK(topic is NOT NULL or course_offering is NOT NULL),
    FOREIGN KEY(topic) REFERENCES topics(id),
    FOREIGN KEY(course_offering) REFERENCES course_offerings(id)
);


DROP TABLE IF EXISTS course_offerings;
CREATE TABLE course_offerings(
    id          INTEGER NOT NULL PRIMARY KEY,
    course      INTEGER NOT NULL,
    session     INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY(course) REFERENCES courses(id),
    FOREIGN KEY(session) REFERENCES sessions(id)
);


DROP TABLE IF EXISTS course_roles;
CREATE TABLE course_roles(
    id          INTEGER NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS courses;
CREATE TABLE courses(
    id          INTEGER NOT NULL PRIMARY KEY,
    code        TEXT NOT NULL,
    name        TEXT NOT NULL,
    description TEXT,
    prereq      INTEGER
);


DROP TABLE IF EXISTS enrollments;
CREATE TABLE enrollments(
    user            INTEGER NOT NULL,
    course_offering INTEGER NOT NULL,
    role            INTEGER,
    FOREIGN KEY(user) REFERENCES users(id),
    FOREIGN KEY(course_offering) REFERENCES course_offerings(id),
    FOREIGN KEY(role) REFERENCES course_roles(id)
);


DROP TABLE IF EXISTS file_types;
CREATE TABLE file_types(
    id          INTEGER NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS marking_methods;
CREATE TABLE marking_methods(
    id          INTEGER NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS marks;
CREATE TABLE marks(
    criteria INTEGER NOT NULL,
    mark      INTEGER,
    student   INTEGER NOT NULL,
    marker    INTEGER NOT NULL,
    feedback  TEXT,
    file_path TEXT,
    PRIMARY KEY(criteria, student, marker),
    FOREIGN KEY(criteria) REFERENCES task_criteria(id),
    FOREIGN KEY(student) REFERENCES users(id),
    FOREIGN KEY(marker) REFERENCES users(id)
);


DROP TABLE IF EXISTS material_attachments;
CREATE TABLE material_attachments(
    id       INTEGER NOT NULL PRIMARY KEY,
    material INTEGER NOT NULL,
    path     TEXT NOT NULL,
    FOREIGN KEY(material) REFERENCES materials(id)
);


DROP TABLE IF EXISTS materials;
CREATE TABLE materials(
    id              INTEGER NOT NULL PRIMARY KEY,
    course_offering INTEGER NOT NULL,
    name            TEXT NOT NULL,
    visible         INTEGER DEFAULT 1,
    description     TEXT,
    FOREIGN KEY(course_offering) REFERENCES course_offerings(id)
);


DROP TABLE IF EXISTS prerequisites;
CREATE TABLE prerequisites(
    id     INTEGER NOT NULL PRIMARY KEY,
    type   INTEGER NOT NULL,
    mark   INTEGER,
    topic  INTEGER NOT NULL,
    course INTEGER NOT NULL,
    FOREIGN KEY(topic) REFERENCES topics(id),
    FOREIGN KEY(course) REFERENCES courses(id)
);


DROP TABLE IF EXISTS request_statuses;
CREATE TABLE request_statuses(
    id          INTEGER NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions(
    id         INTEGER NOT NULL PRIMARY KEY,
    start_date INTEGER,
    end_date   INTEGER,
    year       INTEGER NOT NULL,
    term       INTEGER NOT NULL
);


DROP TABLE IF EXISTS student_topic;
CREATE TABLE student_topic(
    student  INTEGER NOT NULL,
    topic    INTEGER NOT NULL,
    assessor INTEGER,
    PRIMARY KEY(student, topic),
    FOREIGN KEY(student) REFERENCES users(id),
    FOREIGN KEY(topic) REFERENCES topics(id),
    FOREIGN KEY(assessor) REFERENCES users(id)
);


DROP TABLE IF EXISTS submission_methods;
CREATE TABLE submission_methods(
    id          INTEGER NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS submission_types;
CREATE TABLE submission_types(
    file_type INTEGER NOT NULL,
    task      INTEGER NOT NULL,
    PRIMARY KEY(file_type, task),
    FOREIGN KEY(file_type) REFERENCES file_types(id),
    FOREIGN KEY(task) REFERENCES tasks(id)
);


-- currently only allows for 1 submission file, can change later
-- but seems fine for thesis assessments
DROP TABLE IF EXISTS submissions;
CREATE TABLE submissions(
    student       INTEGER NOT NULL,
    task          INTEGER NOT NULL,
    name          TEXT NOT NULL,
    path          TEXT,
    text          TEXT,
    date_modified INTEGER NOT NULL,
    status        INTEGER NOT NULL,
    PRIMARY KEY(student, task),
    FOREIGN KEY(student) REFERENCES users(id),
    FOREIGN KEY(task) REFERENCES tasks(id),
    FOREIGN KEY(status) REFERENCES request_statuses(id)
);


DROP TABLE IF EXISTS tasks;
CREATE TABLE tasks(
    id                 INTEGER NOT NULL PRIMARY KEY,
    name               TEXT NOT NULL,
    course_offering    INTEGER NOT NULL,
    deadline           INTEGER NOT NULL,
    description        TEXT,
    size_limit         INTEGER DEFAULT 5, -- in MB's --
    visible            INTEGER DEFAULT 1,
    submission_method  INTEGER DEFAULT 0,
    marking_method     INTEGER DEFAULT 0,
    word_limit         INTEGER DEFAULT 1000,
    FOREIGN KEY(marking_method) REFERENCES marking_methods(id),
    FOREIGN KEY(submission_method) REFERENCES submission_methods(id),
    FOREIGN KEY(course_offering) REFERENCES course_offerings(id)
);


DROP TABLE IF EXISTS task_attachments;
CREATE TABLE task_attachments(
    id   INTEGER NOT NULL PRIMARY KEY,
    task INTEGER NOT NULL,
    path TEXT NOT NULL,
    FOREIGN KEY(task) REFERENCES tasks(id)
);


DROP TABLE IF EXISTS task_criteria;
CREATE TABLE task_criteria(
    id          INTEGER NOT NULL PRIMARY KEY,
    task        INTEGER NOT NULL,
    name        TEXT NOT NULL,
    description TEXT,
    max_mark    INTEGER NOT NULL,
    FOREIGN KEY(task) REFERENCES tasks(id)
);


DROP TABLE IF EXISTS topics;
CREATE TABLE topics(
    id          INTEGER NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    supervisor  INTEGER NOT NULL,
    visible     INTEGER DEFAULT 1,
    description TEXT NOT NULL,
    FOREIGN KEY(supervisor) REFERENCES users(id)
);


DROP TABLE IF EXISTS topic_to_area;
CREATE TABLE topic_to_area(
    topic       INTEGER NOT NULL,
    topic_area  INTEGER NOT NULL,
    PRIMARY KEY(topic, topic_area),
    FOREIGN KEY(topic) REFERENCES topics(id),
    FOREIGN KEY(topic_area) REFERENCES topic_areas(id)
);


DROP TABLE IF EXISTS topic_areas;
CREATE TABLE topic_areas(
    id          INTEGER NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT
);


DROP TABLE IF EXISTS topic_requests;
CREATE TABLE topic_requests(
    student        INTEGER NOT NULL,
    topic          INTEGER NOT NULL,
    status         INTEGER NOT NULL,
    date_created   INTEGER NOT NULL,
    text           TEXT NOT NULL,
    date_responded INTEGER,
    PRIMARY KEY(student, topic),
    FOREIGN KEY(student) REFERENCES users(id),
    FOREIGN KEY(topic) REFERENCES topics(id),
    FOREIGN KEY(status) REFERENCES request_statuses(id)
);


DROP TABLE IF EXISTS update_account_types;
CREATE TABLE update_account_types(
    id              INTEGER NOT NULL PRIMARY KEY,
    new_name        TEXT NOT NULL,
    email           TEXT NOT NULL,
    account_type    INTEGER NOT NULL,
    course_offering INTEGER,
    FOREIGN KEY(account_type) REFERENCES account_types(id),
    FOREIGN KEY(course_offering) REFERENCES course_offerings(id)
);


DROP TABLE IF EXISTS users;
CREATE TABLE users(
    id           INTEGER NOT NULL PRIMARY KEY,
    name         TEXT NOT NULL,
    email        TEXT NOT NULL,
    password     TEXT NOT NULL,
    account_type INTEGER,
    confirm_code TEXT NOT NULL,
    date_created INTEGER NOT NULL,
    FOREIGN KEY(account_type) REFERENCES account_types(id)
);
