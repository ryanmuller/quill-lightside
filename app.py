from sys import argv
import bottle
from bottle import route, static_file

@route('/')
def root():
    return static_file("app.html", root="./static/")


@route('/assets/<filepath:path>')
def asset(filepath):
    return static_file(filepath, root="./static/")

bottle.run(host='0.0.0.0', port=argv[1])
