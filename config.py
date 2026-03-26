import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY', 'goodhost-secret-key-2026')
DATABASE = os.path.join(BASE_DIR, 'database.db')

# Email – задай тези env variables преди стартиране:
#   set MAIL_USERNAME=твоят_gmail@gmail.com
#   set MAIL_PASSWORD=app_password_от_gmail
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
