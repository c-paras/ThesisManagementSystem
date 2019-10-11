  
from flask import Flask, render_template,session, request, Response, url_for, redirect
from flask_restful import Resource, Api, reqparse, fields, marshal

app = Flask(__name__)

@app.route('/')
def base():
    return render_template('base.html') #loads base for now to be changes


if __name__ == '__main__':
    app.run(use_reloader=False, debug=True)





