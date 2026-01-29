import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Core Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Admin Credentials (Dev/Windows Fallback)
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    # Secure default: If no password set, disable default login by generating random
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    if not ADMIN_PASSWORD:
        import uuid
        ADMIN_PASSWORD = str(uuid.uuid4())
    
    # Database
    _db_uri = os.getenv('DATABASE_URL', 'sqlite:///squid_manager.db')
    if _db_uri.startswith('sqlite:///'):
        _db_path = _db_uri.replace('sqlite:///', '')
        if not os.path.isabs(_db_path):
            _db_path = os.path.join(basedir, _db_path)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + _db_path
    else:
        SQLALCHEMY_DATABASE_URI = _db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Squid Configuration
    SQUID_CONF_DIR = os.getenv('SQUID_CONF_DIR', '/etc/squid/conf.d/')
    SQUID_DOMAINS_DIR = os.getenv('SQUID_DOMAINS_DIR', '/etc/squid/domains/')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output/')

    # Logging
    LOGGING_DIR = os.getenv('LOGGING_DIR', 'logs/')
    LOG_FILE = os.path.join(LOGGING_DIR, 'apply_configuration.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    # Application Settings
    MAX_CLIENTS = int(os.getenv('MAX_CLIENTS', 100))
    WEBSITE_NAME = os.getenv('WEBSITE_NAME', 'Squid Manager')
    
    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.getenv('SESSION_LIFETIME_MINUTES', 15)))

    # Scheduler & Network
    JOB_HOUR = int(os.getenv('JOB_HOUR', 17))
    JOB_MINUTE = int(os.getenv('JOB_MINUTE', 3))
    DNS_SERVER = os.getenv('DNS_SERVER', '10.30.110.1')

def create_app():
    from flask import Flask
    
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints (Old structure, will be refactored in Phase 2)
    # Note: 'auth' and 'log' are imported in __init__.py in the original code,
    # but here we ensure they are registered if create_app is used directly.
    # Ideally, __init__.py handles this. This file mainly provides Config.
    
    # Keeping the imports minimal here to avoid circular dependencies if this file is imported by __init__
    
    return app
