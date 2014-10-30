from sys import argv
import bottle
from bottle import get, post, static_file, request
from lightbox import *

@get('/')
def root():
    return static_file("app.html", root="./static/")

@get('/assets/<filepath:path>')
def asset(filepath):
    return static_file(filepath, root="./static/")

@get('/lightboxes/<lightbox_id>')
def lightbox(lightbox_id):
    lightbox = Lightbox.find(lightbox_id)
    grader = lightbox.grader()
    prompt = grader.prompt()
    return { 'name': lightbox.name(),
             'prompt': prompt.text() }

@post('/lightboxes/<lightbox_id>/answers')
def answer(lightbox_id):
    lightbox = Lightbox.find(lightbox_id)
    answer_set = lightbox.answer_set()
    answer = Answer.create(1, answer_set._id, request.forms.get('text'))
    prediction_task = PredictionTask.create(answer_set._id)
    prediction_task.process()
    return { 'answer_id': answer._id }

@get('/answers/<answer_id>/result')
def result(answer_id):
    answer = Answer.find(answer_id)
    result = answer.prediction_result()

    if result:
        return { 'label': result.label() }
    else:
        return {}

bottle.run(host='0.0.0.0', port=argv[1])
