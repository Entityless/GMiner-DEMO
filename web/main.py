import flask
from flask import request
import json
import subprocess
import time, os

from gminer_infos import *
import gminer_infos
import utils.ini_generator

app = flask.Flask(__name__)
app_table = {}
manager_table = {}

def get_timestamp():
    t = time.time()
    t = int(t * 1000 + 0.5);
    return t

@app.route('/')
def main():
    image = [1,2,3,4,5,6,7,8,9]
    persons = gminer_infos.gminer_persons * 7;
    persons = [persons[i * 2:i * 2 + 2] for i in range(7//2 + 1)]
    return flask.render_template('index.html', apps=gminer_apps,
            datasets=gminer_datasets, sysconfigs0=gminer_sysconfig[:3],
            sysconfigs1=gminer_sysconfig[3:], slideimages = image, teammembers = persons)

@app.route('/load_json/<folder>/<path>')
def return_cpu_info(folder, path):
    path = os.path.join(folder, path)
    with open(path) as f:
        res = json.load(f)
    resp = flask.Response(json.dumps(res), mimetype='application/json')
    return resp

@app.route('/runrequest', methods=['POST'])
def runApplication():
    timestamp = get_timestamp()
    myenv = os.environ.copy()
    # try:
    data = json.loads(request.data)
    print(data)
    # 1. run python manager
    proc = subprocess.Popen(['python', 'utils/gminer-manager.py', '-t', str(timestamp)], stdout=subprocess.DEVNULL)
    manager_table[timestamp] = proc
    # 2. run gminer
    cmd, ini_str = utils.ini_generator.gminer_ini_gen(data)
    myenv['GMINER_INI_NAME'] = os.path.join(myenv['GMINER_HOME'], 'tmp', str(timestamp)+'.ini')
    myenv['GMINER_START_TIMESTAMP'] = timestamp
    with open(myenv['GMINER_INI_NAME'], 'w') as f:
        f.write(ini_str)

    cmd = cmd.format(str(timestamp))
    print('run command: ', cmd)
    final_cmd = 'GMINER_INI_NAME={} GMINER_START_TIMESTAMP={} {}'.\
            format(myenv['GMINER_INI_NAME'], myenv['GMINER_START_TIMESTAMP'], cmd)
    proc = subprocess.Popen(final_cmd, shell=True, stdout=subprocess.DEVNULL)
    app_table[timestamp] = proc

    data = {'key': timestamp, 'status': "ok"}
    # except Exception, e:
    #     data = {'key': timestamp, 'status': "stop"}
    #     print(e)
    
    resp = flask.Response(json.dumps(data), mimetype='application/json')
    return resp

@app.route('/stoprequest', methods=['POST'])
def kill_by_timestamp():
    data = json.loads(request.data)
    key = data['key']
    app_table[key].kill()
    manager_table[key].kill()
    del app_table[key]
    
    data = {'key': key, 'status': "stop"}
    resp = flask.Response(json.dumps(data), mimetype='application/json')
    return resp

@app.route('/interaction', methods=['POST'])
def send_infos():
    data = json.loads(request.data)
    print('recv interaction ',data)
    key = data["key"]
    res = {}
    fname = os.path.join('runtime-infos', '{}.log'.format(key))
    stdpt = int(data['stdpt'])
    # 1. read stdout file
    with open(fname) as f:
        f.seek(stdpt)
        res['text'] = f.read()
        stdpt = f.tell()
        res['stdpt'] = stdpt
    res['text'] = res['text'].replace('\n', '<br>')

    # 2. read queue data
    que = 'runtime-infos/{}/master_5q.json'.format(key)
    with open(que) as f:
        que = json.load(f)
        res.update(que)

    # 3. read system info
    
    # 4. read graph info
    fname = 'runtime-infos/{}/slaves.json'.format(key)
    if os.path.exists(fname):
        with open(fname) as f:
            graph = json.load(f);
            res.update(graph)
    # 5. if end
    res['end'] = 0 if app_table[int(key)].poll() is None else 1
    respon = flask.Response(json.dumps(res), mimetype='application/json')
    res['text'] = 'deleted'
    print('interaction info:', res)
    return respon

