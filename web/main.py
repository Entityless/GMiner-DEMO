import flask
from flask import request
import json
import subprocess
import time

from gminer_infos import *
import utils.ini_generator

app = flask.Flask(__name__)
app_table = {}

def get_timestamp():
    t = time.time()
    t = int(t * 1000 + 0.5);
    return t

@app.route('/')
def main():
    return flask.render_template('index.html', apps=gminer_apps,
            datasets=gminer_datasets, sysconfigs0=gminer_sysconfig[:3],
            sysconfigs1=gminer_sysconfig[3:])

@app.route('/load_json/<folder>/<path>')
def return_cpu_info(folder, path):
    path = os.path.join(folder, path)
    with open(path) as f:
        res = json.load(f)
    resp = flask.Response(json.dumps(res), mimetype='application/json')
    return resp

@app.route('/runrequest', methods=['POST'])
def runApplication():
    ini_pat='GMINER_INI_NAME={}.ini'
    data = dict(request.form)
    cmd, ini_str = utils.ini_generator.gminer_ini_gen(param_dic)
    timestamp = get_timestamp()
    with open(str(timestamp), 'w') as f:
        f.write(ini_str)

    cmd = cmd.format(str(timestamp))
    cmd = cmd.split()
    cmd = [ini_pat.format(str(timestamp))] + cmd
    print('run command: ', cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    app_table[timestamp] = proc

    data = {'key': timestamp, 'status': "ok"}
    resp = flask.Response(json.dumps(data), mimetype='application/json')
    return resp
