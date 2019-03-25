import sys
import os
sys.path.append(
    os.path.join(os.path.dirname(__file__), '../lib/')
)

from flask import Flask, request, render_template, jsonify, send_file
import spacy

from query import Searcher

SPACY_MODEL = 'en_vectors_web_lg'

app = Flask('identifier')

def relative_path(end_of_path):
    return os.path.join(os.path.dirname(__file__), end_of_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_file(relative_path('favicon.ico'), mimetype='image/png')

@app.route('/index.js')
def script():
    return send_file(relative_path('index.js'), mimetype='application/javascript')

@app.route('/index.css')
def stylesheet():
    return send_file(relative_path('index.css'), mimetype='text/css')

@app.route('/identify')
def identify():
    return jsonify({
        'result': searcher.query(
            request.args.get('query'),
            limit=6
        )
    })

print('instantiating searcher...')
searcher = Searcher(
    spacy.load(SPACY_MODEL)
)
print('...done instantiating searcher.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
