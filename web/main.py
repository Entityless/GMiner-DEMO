import flask
from flask import request
import json
import subprocess
import time

from gminer_infos import *
app = flask.Flask(__name__)
app_table = {}

def get_timestamp():
    t = time.time()
    t = int(t * 1000 + 0.5);
    return t

def set_cmd(param):
    pass
@app.route('/')
def main():
    return flask.render_template('index.html', apps=gminer_apps,
            datasets=gminer_datasets, sysconfigs0=gminer_sysconfig[:3],
            sysconfigs1=gminer_sysconfig[3:])

@app.route('/runrequest', methods=['POST'])
def runApplication():
    data = dict(request.form)
    cmd = set_cmd(data)
    print(type(data))
    timestamp = get_timestamp()
    data = {'key': timestamp, 'status': "ok"}
    resp = flask.Response(json.dumps(data), mimetype='application/json')
    return resp
