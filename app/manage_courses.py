import json

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from flask import session

from app.auth import UserRole
from app.auth import at_least_role
from app.db_manager import sqliteManager as db
from app.queries import queries


manage_courses = Blueprint('manage_courses', __name__)

# allow for a defaults course or don't reset which course they are on
# and reformat the name so it looks better in list
@manage_courses.route('/manage_courses', methods=['GET', 'POST'])
@at_least_role(UserRole.COURSE_ADMIN)
def manage_course_offerings():
    if request.method == 'GET':
        db.connect()
        courses = queries.get_course_offering_details()
        db.close()
        # return render_template('manage_courses.html',
        #                        materials=[],
        #                        tasks=[],
        #                        enrollments=[],
        #                        courses=courses)

    # data = json.loads(request.data)
    co = 1
    db.connect()
    courses = queries.get_course_offering_details()
    materialsQuery = db.select_columns(
        'materials', ['id', 'name', 'visible'], ['course_offering'], [co]
    )
    materials = []
    for material in materialsQuery:
        attachments = []
        attachmentsQuery = db.select_columns(
            'material_attachments', ['path'], ['material'], [material[0]]
        )
        attachments = [x[0] for x in attachmentsQuery]
        materials.append((material[0], material[1], attachments, material[2]))
    db.close()
    return render_template(
        'manage_courses.html',
        materials=materials,
        tasks=[],
        enrollments=[],
        courses=courses)
