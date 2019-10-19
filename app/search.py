from flask import Blueprint
from flask import render_template
from flask import session

from app.auth import loggedin

search = Blueprint('search', __name__)


@search.route('/search', methods=['GET', 'POST'])
@loggedin
def searchTopic():
    return render_template('search.html',
                           heading='Search Topics', title='Search Topics')
