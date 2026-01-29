from flask import Flask, send_from_directory
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_talisman import Talisman
from app.extensions import db, csrf
from app.models.user import User  # Import User model
from config import Config
from app.services.auto_tasks import auto_generate_and_apply_config
from datetime import datetime

import os
import logging

login_manager = LoginManager()
scheduler = APScheduler()
# Cấu hình logging
logging.basicConfig(
    filename='logs/application.log',  # Đường dẫn file log
    level=logging.DEBUG,               # Mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Định dạng log
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Security Headers (Flask-Talisman)
    # Note: content_security_policy is set to None for now to avoid breaking Tailwind CDN,
    # but HSTS and other headers are enabled.
    Talisman(app, 
        content_security_policy=None,
        force_https=False  # Allow HTTP for local development (set to True in prod via Env if needed)
    )

    # Register custom filter
    @app.template_filter('strftime')
    def format_datetime(value, format='%d-%m-%Y'):
        if isinstance(value, datetime):
            return value.strftime(format)
        return value
    
    # Truyền biến cấu hình vào tất cả các template
    @app.context_processor
    def inject_config():
        return dict(config=app.config)
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Khởi tạo APScheduler
    scheduler.init_app(app)
    scheduler.start()

    # Định nghĩa job định kỳ
    scheduler.add_job(
        id='daily_generate_and_apply_config',
        func=lambda: auto_generate_and_apply_config(app),  # Truyền app vào hàm
        trigger='cron',
        hour=app.config['JOB_HOUR'],  # Lấy giờ từ config
        minute=app.config['JOB_MINUTE']  # Lấy phút từ config
    )

    # Initialize Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)  # Tải user từ ID

    # Đăng ký các blueprint
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.blueprints.clients import clients_bp
    app.register_blueprint(clients_bp)

    from app.blueprints.configuration import configuration_bp
    app.register_blueprint(configuration_bp)

    from app.blueprints.logs import log_bp
    app.register_blueprint(log_bp, url_prefix='/log')

    from app.blueprints.whitelist import whitelist_bp
    app.register_blueprint(whitelist_bp)

    # Import all models to ensure they are registered before create_all
    from app.models import Client, GlobalDomainWhitelist, GlobalIPWhitelist, DomainTemplate
    
    # Create database tables (if not exist)
    with app.app_context():
        db.create_all()

    return app