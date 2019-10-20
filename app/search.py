from flask import Blueprint
from flask import render_template
from flask import session
from flask import request
from flask import jsonify
import json

from app.auth import loggedin
from app.db_manager import sqliteManager as db
from app.helpers import get_fields

search = Blueprint('search', __name__)


@search.route('/search', methods=['GET', 'POST'])
@loggedin
def searchTopic():
    if request.method == 'GET':
        return render_template('search.html',
                               heading='Search Topics', title='Search Topics')

    searchTopic = list(dict.fromkeys(request.form.getlist('tagsTopic')))
    searchSuper = list(dict.fromkeys(request.form.getlist('tagsSupervisor')))
    searchTopic = list(filter(None, searchTopic))
    searchSuper = list(filter(None, searchSuper))
    searchTerms = request.form.get('search')
    searchCheck = request.form.get('checkbox-vis')

    print("search terms are")
    print(searchTopic)
    print(searchSuper)
    print(searchTerms)
    print(searchCheck)

    db.connect()
    print("hello")
    res = db.select_columns('topics',
                            ['id', 'name', 'supervisor', 'description'], None, None)
    print(json.dumps(res))
    supervisor = []
    for topic in res:
        supervisor.append(db.select_columns('users', ['name'],
                                            ['id'], [topic[2]])[0][0])
    print(json.dumps(supervisor))

    topicAreas = db.select_columns('topic_areas',
                                   ['name', 'topic'], None, None)
    print(topicAreas)
    return jsonify({'status': 'ok', 'topics': res, 'supervisor': supervisor})
