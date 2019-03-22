import sys
sys.path.append('../lib/')

from flask import Flask, request, render_template, jsonify, send_file
import spacy

from query import Searcher

SPACY_MODEL = 'en_vectors_web_lg'

app = Flask('identifier')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico', mimetype='image/png')

@app.route('/index.js')
def script():
    return send_file('index.js', mimetype='application/javascript')

@app.route('/index.css')
def stylesheet():
    return send_file('index.css', mimetype='text/css')

@app.route('/identify')
def identify():
    return jsonify({
        'result': searcher.query(
            request.args.get('query'),
            limit=6
        )
    })

searcher = Searcher(spacy.load(SPACY_MODEL))

if __name__ == '__main__':
    app.run()
