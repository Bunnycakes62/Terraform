'''
#
# Web Server functions for CES592, assignment #13.
#
# Version 1.0 - Initial Version
#
'''

import json
from bottle import abort, route, response, request, run
import boto3
from db import Database, Schedule


@route('/')
def index():
    response.set_header('Content-Type', 'application/vnd.api+json')
    return json.dumps({'res': 'success'})


@route('/all')
def index():
    db = Database('aws')

    response.set_header('Content-Type', 'application/vnd.api+json')

    data = []
    for item in Schedule.select():
        data.append({
            'id': item.instance_id,
            'start at': str(item.start_at),
            'stop at': str(item.stop_at)
        })

    return json.dumps(data)


@route('/add/<instance_id>')
def index(instance_id):
    start_at = request.query.start_at
    end_at = request.query.end_at

    try:
        db = Database('aws')

        Schedule.add(instance_id, start_at, end_at)
        response.set_header('Content-Type', 'application/vnd.api+json')
        return json.dumps({'res': 'success'})
    except Exception as ex:
        abort(500, str(ex))


@route('/del/<instance_id>')
def index(instance_id):
    try:
        db = Database('aws')

        item = Schedule.remove(instance_id)
        response.set_header('Content-Type', 'application/vnd.api+json')
        return json.dumps({'res': 'success'})
    except Exception as ex:
        abort(500, str(ex))


run(host='0.0.0.0', port=8080)
