DELETE FROM course_roles;
INSERT INTO course_roles (name, description) VALUES ('student', 'TODO');
INSERT INTO course_roles (name, description) VALUES ('staff', 'TODO');

DELETE FROM account_types;
INSERT INTO account_types (name, description) VALUES ('student', 'TODO');
INSERT INTO account_types (name, description) VALUES ('course_admin', 'TODO');
INSERT INTO account_types (name, description) VALUES ('supervisor', 'TODO');

DELETE FROM file_types;
INSERT INTO file_types (name, description) VALUES ('.pdf', 'TODO');
INSERT INTO file_types (name, description) VALUES ('.txt', 'TODO');
INSERT INTO file_types (name, description) VALUES ('.zip', 'TODO');
INSERT INTO file_types (name, description) VALUES ('.tar', 'TODO');

DELETE FROM marking_methods;
INSERT INTO marking_methods (name, description) VALUES ('text submission', 'TODO');
INSERT INTO marking_methods (name, description) VALUES ('file submission', 'TODO');

DELETE FROM request_statuses;
INSERT INTO request_statuses (name, description) VALUES ('pending', 'TODO');
INSERT INTO request_statuses (name, description) VALUES ('approved', 'TODO');
INSERT INTO request_statuses (name, description) VALUES ('rejected', 'TODO');
INSERT INTO request_statuses (name, description) VALUES ('marked', 'TODO');
INSERT INTO request_statuses (name, description) VALUES ('pending mark', 'TODO');
INSERT INTO request_statuses (name, description) VALUES ('cancelled', 'TODO');

DELETE FROM courses;
INSERT INTO courses (code, name) VALUES ('COMP3231', 'Operating Systems');
INSERT INTO courses (code, name) VALUES ('COMP3311', 'Database Systems');
INSERT INTO courses (code, name) VALUES ('COMP3331', 'Computer Networks and Applications');
INSERT INTO courses (code, name) VALUES ('COMP3411', 'Artificial Intelligence');
INSERT INTO courses (code, name) VALUES ('COMP3421', 'Computer Graphics');
INSERT INTO courses (code, name) VALUES ('COMP3431', 'Robotic Software Architecture');
INSERT INTO courses (code, name) VALUES ('COMP3511', 'Human Computer Interaction');


DELETE FROM users; -- Each has a password of 'password1'


INSERT INTO users (name, email, password, account_type) VALUES ('z0123456', 'z0123456@unsw.edu.au', X'243262243132245072764c6a62412f6253665134766a54757059636e756470414b6f324d7461563765382e642f676a55676b4b53677a75334862732e', (SELECT id FROM account_types WHERE name='student'));

-- Topics
DELETE FROM topics;
DELETE FROM topic_areas;


INSERT INTO users (name, email, password, account_type) VALUES ('z7654321', 'z7654321@unsw.edu.au',X'2432622431322457514545705a2f4f5a4b7275776a6d6b783254352e2e4e517246433861746f4e4e4e797033365766793852507a5a636e3570373771', (SELECT id FROM account_types WHERE name='supervisor'));

INSERT INTO topics (name, supervisor, description) VALUES (
       'Improve the Moodle Page',
       (SELECT id FROM users WHERE name='z7654321'),
       'Research and find any shortcomings with the Moodle interface and implement them');

CREATE TEMP VIEW improve_moodle AS
       SELECT id FROM topics WHERE name='Improve the Moodle Page';

INSERT INTO topic_areas (name, topic) VALUES (
       'User Interfaces',
       (SELECT id from improve_moodle));


INSERT INTO topics (name, supervisor, description) VALUES (
       'Research and improve the material design language',
       (SELECT id FROM users WHERE name='z7654321'),
       'Involves researching the material design language and trying to find any improvements that can be made');
CREATE TEMP VIEW improve_material AS
       SELECT id FROM topics WHERE name='Research and improve the material design language';

INSERT INTO topic_areas (name, topic) VALUES (
       'User Interfaces',
       (SELECT id FROM improve_material));


INSERT INTO users (name, email, password, account_type) VALUES ('z0001112','z0001112@unsw.edu.au',X'243262243132244343704d56534e3177663345624643393262445471652f766a376f4c536d3733666d747466654d4b58587571416f2e564632723957', (SELECT id FROM account_types WHERE name='supervisor'));


INSERT INTO topics (name, supervisor, description) VALUES (
       '3D Visualisation of Robot Sensor Data',
       (SELECT id FROM users WHERE name='z0001112'),
       'Our rescue robot has sensors that can create 3D representations of their surroundings. In a rescue, it is helpful for the incident commander to have a graphical visualisation of the data so that he or she can reconstruct the disaster site.');

CREATE TEMP VIEW three_visual AS
       SELECT id FROM topics WHERE name='3D Visualisation of Robot Sensor Data';

INSERT INTO topic_areas (name, topic) VALUES (
       'Graphics',
       (SELECT id FROM three_visual));

INSERT INTO topic_areas (name, topic) VALUES (
       'Robotics',
       (SELECT id FROM three_visual));