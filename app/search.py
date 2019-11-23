from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
from flask import session

from app.auth import at_least_role
from app.auth import UserRole
from app.db_manager import sqliteManager as db
from app.queries import queries
from app.update_accounts import get_all_account_types

import re
import json

import config


search = Blueprint('search', __name__)


@search.route('/search', methods=['GET', 'POST'])
@at_least_role(UserRole.PUBLIC)
def search_topic():
    if request.method == 'GET':
        search_term = request.args.get('search')
        return render_template('search.html',
                               topic_request_text=config.TOPIC_REQUEST_TEXT,
                               heading='Search Topics', title='Search Topics',
                               search_term=search_term)

    # getting input from forms
    data = json.loads(request.data)
    search_topic = [topic['tag'] for topic in data['topicArea']]
    search_super = [supers['tag'] for supers in data['supervisor']]
    search_term = data['searchTerm']
    search_check = data['checkbox']

    db.connect()

    # getting submitted topic_area
    topic_area = []
    if len(search_topic) > 0:
        for area in search_topic:
            topic_area.append(queries.search_topic_areas(area))

    # getting submitted supervisors
    supervisor = []
    if len(search_super) > 0:
        for sup in search_super:
            supervisor.append(db.select_columns('users', ['name', 'id'],
                                                ['name'], [sup]))

    # getting rid of empty string and empty results
    topic_area = [i for sub in topic_area for i in sub]
    topic_area = [i for i in topic_area if i != []]
    supervisor = [i for sub in supervisor for i in sub]
    supervisor = [i for i in supervisor if i != []]

    # Getting topics that match the topic_area and
    # supervisors if supplied
    # multiple topic_ares and supervisors ar ORed as described in
    # user stories.
    if (len(search_topic) > 0 and len(topic_area) == 0) or\
       (len(search_super) > 0 and len(supervisor) == 0):
        return jsonify({'status': 'ok', 'topics': [],
                        'topicsArea': [],
                        'topicSupervisor': []})

    if len(topic_area) == 0 and len(supervisor) == 0:
        res = db.select_columns('topics',
                                ['id', 'name', 'supervisor',
                                 'description', 'visible'], None, None)
    elif len(topic_area) > 0 and len(supervisor) == 0:
        temp = []
        for area in topic_area:
            temp.append(db.select_columns('topics',
                                          ['id', 'name', 'supervisor',
                                           'description', 'visible'],
                                          ['id'], [area[1]]))
        res = [i for sub in temp for i in sub]
    elif len(topic_area) == 0 and len(supervisor) > 0:
        temp = []
        for sup in supervisor:
            temp.append(db.select_columns('topics',
                                          ['id', 'name', 'supervisor',
                                           'description', 'visible'],
                                          ['supervisor'], [sup[1]]))
        res = [i for sub in temp for i in sub]

    elif len(topic_area) > 0 and len(supervisor) > 0:
        temp = []
        for sup in supervisor:
            for area in topic_area:
                temp.append(db.select_columns('topics',
                                              ['id', 'name', 'supervisor',
                                               'description', 'visible'],
                                              ['supervisor', 'id'],
                                              [sup[1], area[1]]))
        res = [i for sub in temp for i in sub]

    topics = []
    for r in res:
        topics.append({
            'id': r[0],
            'title': r[1],
            'supervisor': {
                'id': r[2],
                'name': None,
                'email': None
            },
            'description': r[3],
            'visible': int(r[4]),
            'preqs': []
        })

    matched_search_phrase = []
    if len(search_term) > 0:
        for t in topics:
            if re.search(search_term, t['title'], flags=re.I):
                matched_search_phrase.append(t)
            elif re.search(search_term, t['description'], flags=re.I):
                matched_search_phrase.append(t)
    else:
        matched_search_phrase = topics

    # checking if topics are visible or not
    to_return_searches = []
    if search_check:
        for results in matched_search_phrase:
            if results['visible'] == 1:
                to_return_searches.append(results)
    else:
        to_return_searches = matched_search_phrase

    # Fill in data for found topics
    for topic in to_return_searches:
        res = queries.get_topic_areas(topic['id'])
        topic['areas'] = [r[0] for r in res]

        res = db.select_columns('users',
                                ['name', 'email'],
                                ['id'], [topic['supervisor']['id']])
        topic['supervisor']['name'] = res[0][0]
        topic['supervisor']['email'] = res[0][1]

        res = db.select_columns('prerequisites',
                                ['course'],
                                ['topic'], [topic['id']])
        topic['preqs'] = [{'id': r[0]} for r in res]
        for course in topic['preqs']:
            res = db.select_columns('courses',
                                    ['code'],
                                    ['id'], [course['id']])
            course['code'] = res[0][0]

    sort_req = data.get('sortBy', 'create-ascend')
    reverse = 'descend' in sort_req
    sort_words = {
        'create': lambda t: t['id'],
        'title': lambda t: t['title'],
        'supervisor': lambda t: t['supervisor']['name']
    }
    # Retrieve the function from the above dictionary if the requested
    # sort by parameter is one of the keys, defaults to create
    sort_function = next((f for k, f in sort_words.items() if k in sort_req),
                         sort_words['create'])
    to_return_searches = sorted(to_return_searches,
                                key=sort_function, reverse=reverse)

    return jsonify({'status': 'ok', 'topics': to_return_searches,
                    'canRequest': session['acc_type'] == 'student'})


@search.route('/search_chips', methods=['GET'])
@at_least_role(UserRole.PUBLIC)
def get_chips():
    db.connect()
    topic_area = db.select_columns('topic_areas', ['name'])
    account_types = get_all_account_types()
    supervisors = db.select_columns(
        'users', ['name'], ['account_type'], [account_types['supervisor']]
    )
    supervisors += db.select_columns(
        'users', ['name'], ['account_type'], [account_types['course_admin']]
    )

    chips_topic_area = {}
    for topic in topic_area:
        chips_topic_area[topic[0]] = None

    chips_supervisor = {}
    for sup in supervisors:
        chips_supervisor[sup[0]] = None

    return jsonify({'status': 'ok', 'chipsTopic': chips_topic_area,
                    'chipsSuper': chips_supervisor})
