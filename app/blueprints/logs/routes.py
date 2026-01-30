from flask import Blueprint, render_template, request
from flask_login import login_required
from app.services.log_service import LogService

log_bp = Blueprint('log', __name__)

@log_bp.route('/', methods=['GET', 'POST'])
@login_required
def log():
    ip_filter = request.args.get('ip_filter', '').strip() if request.method == 'GET' else request.form.get('ip_filter', '').strip()
    status_filter = request.args.get('status_filter', 'ANY').strip() if request.method == 'GET' else request.form.get('status_filter', 'ANY').strip()

    logs = LogService.get_logs(ip_filter, status_filter)

    return render_template('log.html', logs=logs, ip_filter=ip_filter, active_tab='log')
