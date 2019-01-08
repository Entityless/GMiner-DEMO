import flask
app = flask.Flask(__name__)

@app.route('/')
def main():
    apps = [
            {'tc': {'name':'Triangle Counting', 'param':None}} , 
            {'mc': {'name':'Max Clique', 'param':None}} , 
            {'gm': {'name':'Graph Matching', 'param':None}} , 
            {'cd': {'name': 'Community Detection', 'param': None}}, 
            {'fco': {'name': 'Graph Clustering', 'param': None}}
            ]
    datasets = ['youtube', 'skitter', 'orkut']
    return flask.render_template('index.html', apps=apps, datasets=datasets)

