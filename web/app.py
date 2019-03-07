from flask import Flask, render_template, jsonify, send_file
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
    # return render_template('id_result.json')
    return jsonify({
        'id_result': [
            'A test result name 1',
            'B test result name 2',
            'C test result name 3',
            'D test result name 4',
            'E test result name 5'
        ]
    })

if __name__ == '__main__':
    app.run()
