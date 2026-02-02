import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with secure defaults."""
    
    # Flask Core Settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No FLASK_SECRET_KEY set. Please configure it in .env file")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Settings
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600  # Session expires in 1 hour
    
    # Admin Credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    # Dev Access Key
    DEV_ACCESS_KEY = os.environ.get('DEV_ACCESS_KEY')
    
    # Game Credentials
    GAME_USERNAME = os.environ.get('GAME_USERNAME', '').upper()
    GAME_PASSWORD = os.environ.get('GAME_PASSWORD')
    
    # Security Questions
    SECURITY_ANSWER_1 = os.environ.get('SECURITY_ANSWER_1', '').upper()
    SECURITY_ANSWER_2 = os.environ.get('SECURITY_ANSWER_2', '').upper()
    SECURITY_ANSWER_3 = os.environ.get('SECURITY_ANSWER_3', '').upper()
    
    # 2FA Answer
    TWO_FA_ANSWER = os.environ.get('TWO_FA_ANSWER')
    
    # Final Riddle Answer
    FINAL_RIDDLE_ANSWER = os.environ.get('FINAL_RIDDLE_ANSWER', '').lower()


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


class ProductionConfig(Config):
    """Production configuration with enhanced security."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # Additional production security
    @classmethod
    def init_app(cls, app):
        # Log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the appropriate configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
