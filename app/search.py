from flask import Blueprint
from flask import render_template
from flask import session
from flask import request
from flask import jsonify
import json

from app.auth import loggedin
from app.db_manager import sqliteManager as db

search = Blueprint('search', __name__)


@search.route('/search', methods=['GET', 'POST'])
@loggedin
def searchTopic():
    if request.method == 'GET':
        return render_template('search.html',
                               heading='Search Topics', title='Search Topics')
    
    db.connect()
    print("hello")
    res = db.select_columns('topics', ['name', 'supervisor', 'description'], None, None)
    print(json.dumps(res))
    supervisor = []
    for topic in res:
        supervisor.append(db.select_columns('users', ['name'], ['id'], [topic[1]])[0][0])
    print(json.dumps(supervisor))
    return jsonify({'status': 'ok', 'topics': res, 'supervisor': supervisor})
