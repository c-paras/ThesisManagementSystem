from flask import Blueprint
from flask import render_template
from flask import session
from flask import request
from flask import jsonify
import json
import re

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

    stopWords = ['AND', 'THE', 'WAS', 'IS', 'A', 'WE', 'THAT', 'IN', 'TO']

    # getting input from forms
    searchTopic = list(dict.fromkeys(request.form.getlist('tagsTopic')))
    searchSuper = list(dict.fromkeys(request.form.getlist('tagsSupervisor')))
    searchTopic = list(filter(None, searchTopic))
    searchSuper = list(filter(None, searchSuper))
    searchTerms = request.form.get('search')
    searchCheck = request.form.get('checkbox-vis')

    # cleaning up input
    searchTerms = searchTerms.upper()
    searchTerms = re.split(r"\s+", str(searchTerms))
    searchTerms = list(filter(None, searchTerms))
    searchTerms = [word for word in searchTerms if word not in stopWords]
    db.connect()

    # getting submitted topic_area
    topicAreas = []
    if len(searchTopic) > 0:
        for area in searchTopic:
            topicAreas.append(db.select_columns('topic_areas',
                                                ['name', 'topic'],
                                                ['name'], [area]))
    # getting submitted supervisors
    supervisor = []
    if len(searchSuper) > 0:
        for sup in searchSuper:
            supervisor.append(db.select_columns('users', ['name', 'id'],
                                                ['name'], [sup]))

    # getting rid of empty string and empty results
    topicAreas = [i for sub in topicAreas for i in sub]
    topicAreas = [i for i in topicAreas if i != []]
    supervisor = [i for sub in supervisor for i in sub]
    supervisor = [i for i in supervisor if i != []]

    # Getting topics that match the topic_area and
    # supervisors if supplied
    # multiple topic_ares and supervisors ar ORed as described in
    # user stories.
    if len(searchTopic) > 0 and len(topicAreas) == 0:
        return jsonify({'status': 'ok', 'topics': [],
                        'topicsArea': [],
                        'topicSupervisor': []})
    elif len(searchSuper) > 0 and len(supervisor) == 0:
        return jsonify({'status': 'ok', 'topics': [],
                        'topicsArea': [],
                        'topicSupervisor': []})

    if len(topicAreas) == 0 and len(supervisor) == 0:
        res = db.select_columns('topics',
                                ['id', 'name', 'supervisor',
                                 'description', 'visible'], None, None)
    elif len(topicAreas) > 0 and len(supervisor) == 0:
        temp = []
        for area in topicAreas:
            temp.append(db.select_columns('topics',
                                          ['id', 'name', 'supervisor',
                                           'description', 'visible'],
                                          ['id'], [area[1]]))
        res = [i for sub in temp for i in sub]
    elif len(topicAreas) == 0 and len(supervisor) > 0:
        temp = []
        for sup in supervisor:
            temp.append(db.select_columns('topics',
                                          ['id', 'name', 'supervisor',
                                           'description', 'visible'],
                                          ['supervisor'], [sup[1]]))
        res = [i for sub in temp for i in sub]

    elif len(topicAreas) > 0 and len(supervisor) > 0:
        temp = []
        for sup in supervisor:
            for area in topicAreas:
                temp.append(db.select_columns('topics',
                                              ['id', 'name', 'supervisor',
                                               'description', 'visible'],
                                              ['supervisor', 'id'],
                                              [sup[1], area[1]]))
        res = [i for sub in temp for i in sub]

    # checking if search terms are matched
    matched = [False] * len(res)
    for word in searchTerms:
        for i in range(len(res)):
            if (re.search(word, res[i][1].upper())):
                matched[i] = True

            if (re.search(word, res[i][3].upper())):
                matched[i] = True

    matchedSearchPhrase = []
    if len(searchTerms) == 0:
        matchedSearchPhrase = res
    else:
        for i in range(len(res)):
            if (matched[i]):
                matchedSearchPhrase.append(res[i])

    # checking if topics are visible or not
    toReturnSearches = []
    if searchCheck == 'on':
        for results in matchedSearchPhrase:
            if results[4] == 1:
                toReturnSearches.append(results)
    else:
        toReturnSearches = matchedSearchPhrase

    # getting the topics_areas for the filtered topics
    toReturnTopicArea = []
    for topics in toReturnSearches:
        toReturnTopicArea.append(db.select_columns('topic_areas',
                                                   ['name'],
                                                   ['topic'], [topics[0]]))

    # getting the supervisors for the filtered topics
    toReturnSupervisor = []
    for topics in toReturnSearches:
        toReturnSupervisor.append(db.select_columns('users',
                                                    ['name'],
                                                    ['id'], [topics[2]]))

    return jsonify({'status': 'ok', 'topics': toReturnSearches,
                    'topicsArea': toReturnTopicArea,
                    'topicSupervisor': toReturnSupervisor})
