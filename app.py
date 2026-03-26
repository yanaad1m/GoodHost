import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.database import get_db, init_db
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_email(to_email, subject, body_html):
    if not config.MAIL_USERNAME or not config.MAIL_PASSWORD:
        print(f"[Email не е конфигуриран] До: {to_email} | Тема: {subject}")
        return
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config.MAIL_USERNAME
        msg['To'] = to_email
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))
        with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            server.sendmail(config.MAIL_USERNAME, to_email, msg.as_string())
    except Exception as e:
        print(f"[Email грешка] {e}")


def send_registration_email(to_email, name, user_type):
    role = "домакин" if user_type == "host" else "доброволец"
    body = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;">
      <h2 style="color:#2e7d32;">Добре дошъл в GoodHost, {name}!</h2>
      <p>Регистрацията ти като <strong>{role}</strong> беше успешна.</p>
      <a href="http://localhost:5000/login"
         style="display:inline-block;padding:10px 20px;background:#2e7d32;color:#fff;
                text-decoration:none;border-radius:5px;margin-top:10px;">
        Влез в профила
      </a>
      <p style="margin-top:20px;color:#555;">Екипът на GoodHost</p>
    </div>
    """
    send_email(to_email, "Добре дошъл в GoodHost!", body)


def send_login_email(to_email, name):
    body = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;">
      <h3 style="color:#1565c0;">Нов вход в GoodHost</h3>
      <p>Здравей, {name}! Влязохте в профила си.</p>
      <p>Ако не сте вие, свържете се с нас незабавно.</p>
      <p style="color:#555;">Екипът на GoodHost</p>
    </div>
    """
    send_email(to_email, "Нов вход в профила ти – GoodHost", body)


@app.context_processor
def inject_session():
    return dict(
        is_logged_in='user_id' in session,
        current_user_name=session.get('user_name', ''),
        current_user_type=session.get('user_type', ''),
    )


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
        name             = request.form.get('name', '').strip()
        age              = request.form.get('age', '0')
        email            = request.form.get('email', '').strip().lower()
        phone            = request.form.get('phone', '').strip()
        city             = request.form.get('city', '').strip()
        region           = request.form.get('region', '').strip()
        about            = request.form.get('about', '').strip()
        password         = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        if password != password_confirm:
            flash('Паролите не съвпадат.', 'error')
            return render_template('hostsregistration.html')
        if len(password) < 6:
            flash('Паролата трябва да е поне 6 символа.', 'error')
            return render_template('hostsregistration.html')

        location      = f"{city}, {region}" if region else city
        password_hash = generate_password_hash(password)

        photos = []
        if 'photos' in request.files:
            for f in request.files.getlist('photos')[:3]:
                if f and f.filename and allowed_file(f.filename):
                    filename = f"{int(time.time())}_{secure_filename(f.filename)}"
                    f.save(os.path.join(UPLOAD_FOLDER, filename))
                    photos.append(filename)

        db = get_db()
        try:
            db.execute(
                '''INSERT INTO hosts (name, age, bio, email, phone, location, password_hash, photos)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (name, int(age), about, email, phone, location, password_hash, json.dumps(photos))
            )
            db.commit()
        except Exception as e:
            db.close()
            if 'UNIQUE' in str(e):
                flash('Този имейл вече е регистриран.', 'error')
            else:
                flash('Грешка при регистрацията. Опитай отново.', 'error')
            return render_template('hostsregistration.html')
        db.close()

        send_registration_email(email, name, 'host')
        flash('Регистрацията беше успешна! Вече можеш да влезеш.', 'success')
        return redirect(url_for('login'))

    return render_template('hostsregistration.html')


@app.route('/register/volunteer', methods=['GET', 'POST'])
def volunteer_registration():
    if request.method == 'POST':
        name             = request.form.get('name', '').strip()
        age              = request.form.get('age', '0')
        email            = request.form.get('email', '').strip().lower()
        phone            = request.form.get('phone', '').strip()
        password         = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        if password != password_confirm:
            flash('Паролите не съвпадат.', 'error')
            return render_template('volunteer_registration.html')
        if len(password) < 6:
            flash('Паролата трябва да е поне 6 символа.', 'error')
            return render_template('volunteer_registration.html')

        password_hash = generate_password_hash(password)

        db = get_db()
        try:
            db.execute(
                'INSERT INTO volunteers (name, age, email, phone, password_hash) VALUES (?, ?, ?, ?, ?)',
                (name, int(age), email, phone, password_hash)
            )
            db.commit()
        except Exception as e:
            db.close()
            if 'UNIQUE' in str(e):
                flash('Този имейл вече е регистриран.', 'error')
            else:
                flash('Грешка при регистрацията. Опитай отново.', 'error')
            return render_template('volunteer_registration.html')
        db.close()

        send_registration_email(email, name, 'volunteer')
        flash('Регистрацията беше успешна! Вече можеш да влезеш.', 'success')
        return redirect(url_for('login'))

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
    if 'user_id' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        db = get_db()
        user      = db.execute('SELECT * FROM hosts WHERE email = ?', (email,)).fetchone()
        user_type = 'host'
        if not user:
            user      = db.execute('SELECT * FROM volunteers WHERE email = ?', (email,)).fetchone()
            user_type = 'volunteer'
        db.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id']   = user['id']
            session['user_type'] = user_type
            session['user_name'] = user['name']
            send_login_email(email, user['name'])
            return redirect(url_for('profile'))
        else:
            flash('Грешен имейл или парола.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Трябва да влезеш в профила си.', 'error')
        return redirect(url_for('login'))
    return redirect(url_for('hosts'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
