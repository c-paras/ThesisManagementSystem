from flask import Blueprint
from flask import render_template
from flask import session

from app.auth import loggedin


home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def index():
    if 'user' not in session:
        return render_template('login.html', title='Login', hide_navbar=True)
    else:
        return dashboard()


@home.route('/home', methods=['GET'])
@home.route('/dashboard', methods=['GET'])
@loggedin
def dashboard():
    isStudent = session['accType'] == 'student'
    if(isStudent):
        return studentDashboard()
    else:
        return staffDashboard()


def studentDashboard():
    return render_template('home.html',
                           heading='My Dashboard', title='My Dashboard')


def staffDashboard():
    return render_template('home.html',
                           heading='My Dashboard', title='My Dashboard')
