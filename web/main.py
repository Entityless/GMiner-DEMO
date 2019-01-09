import flask
from gminer_infos import *
app = flask.Flask(__name__)


@app.route('/')
def main():
    return flask.render_template('index.html', apps=gminer_apps,
            datasets=gminer_datasets, sysconfigs0=gminer_sysconfig[:3],
            sysconfigs1=gminer_sysconfig[3:])

