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

# Stripe Identity – sandbox ключове от https://dashboard.stripe.com/test/apikeys
# set STRIPE_SECRET_KEY=sk_test_...
# set STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
