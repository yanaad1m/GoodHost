from flask import Flask
from config import SECRET_KEY
from app.database import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    init_db()

    from app.routes.webhook import webhook_bp
    from app.routes.verify import verify_bp

    app.register_blueprint(webhook_bp)
    app.register_blueprint(verify_bp)

    return app
