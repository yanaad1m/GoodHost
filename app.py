import json
from flask import Flask, render_template, request
from app.database import get_db, init_db

app = Flask(__name__)


@app.template_filter('from_json')
def from_json_filter(value):
    if value:
        try:
            return json.loads(value)
        except Exception:
            return []
    return []


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/registration')
def registration():
    return render_template('registration.html')


@app.route('/hostsregistration', methods=['GET', 'POST'])
def hostsregistration():
    if request.method == 'POST':
        # TODO: обработка на данните от формата
        pass
    return render_template('hostsregistration.html')


@app.route('/register/volunteer', methods=['GET', 'POST'])
def volunteer_registration():
    if request.method == 'POST':
        # TODO: обработка на данните от формата
        pass
    return render_template('volunteer_registration.html')


@app.route('/hosts')
def hosts():
    search = request.args.get('search', '').strip()
    db = get_db()
    if search:
        hosts_list = db.execute(
            'SELECT * FROM hosts WHERE name LIKE ? OR location LIKE ? ORDER BY created_at DESC',
            (f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        hosts_list = db.execute('SELECT * FROM hosts ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('hosts.html', hosts=hosts_list, search=search)


@app.route('/rules')
def rules():
    return render_template('rules.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: обработка на вход
        pass
    return render_template('login.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
