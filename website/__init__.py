from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import os
import sys

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_config

# creating app instance
db = SQLAlchemy()


def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration from config.py (which uses .env)
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    
    db.init_app(app)
    Bootstrap(app)
    
    # Separate routers
    from .auth import auth
    from .views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    
    # Database
    from .modals import User

    create_database(app)
    
    # Login manager with security settings
    login_manager = LoginManager(app)
    login_manager.login_view = 'views.home_page'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'  # Enhanced session security

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def create_database(app):
    if not path.exists("website/instance/database.db"):
        with app.app_context():
            db.create_all()
            print("Database created!")
