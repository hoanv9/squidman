from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from app.models.client import Client
from app.services.system_service import SystemService
from app.services.bandwidth_history_service import BandwidthHistoryService
from sqlalchemy.orm import load_only
from datetime import datetime
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def home():
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Fetch Clients
    clients = Client.query.options(
        load_only(Client.id, Client.ip_address, Client.dns_hostname, Client.expiration_date, Client.date_added)
    ).all()

    # Calculate IP Stats
    total_ips = len(clients)
    active_ips = sum(1 for client in clients if client.expiration_date >= datetime.now().date())
    expired_ips = total_ips - active_ips

    # Calculate Domain Stats
    # Note: Optimization possibility - do this in DB if possible, but keeping logic for now
    total_domains = sum(
        len(client.allowed_domains.split('\n')) for client in clients if client.allowed_domains
    )

    # Fetch System Stats via Service
    server_uptime = SystemService.get_server_uptime()
    squid_status, squid_status_text = SystemService.get_squid_status()
    squid_started_time = SystemService.get_squid_log_time("Starting")
    squid_reload_time = SystemService.get_squid_log_time("Reloading")
    squid_port = SystemService.get_squid_port()

    # Prepare View Data
    all_client_data = []
    for client in clients:
        days_remaining = (client.expiration_date - datetime.now().date()).days
        all_client_data.append({
            'id': client.id,
            'ip_address': client.ip_address,
            'dns_hostname': client.dns_hostname,
            'expiration_date': client.expiration_date.strftime('%d-%m-%Y'),
            'date_added': client.date_added.strftime('%d-%m-%Y'),
            'days_remaining': days_remaining,
            'expired': days_remaining < 0
        })

    # Filter: Expiring within 14 days OR Expired (days_remaining <= 14)
    # Sort: Expired at the bottom.
    # Logic: Sort key tuple (is_expired, days_remaining).
    # False (0) comes before True (1). So active clients come first.
    # Then sort by days_remaining for active ones (asc).
    filtered_client_data = [c for c in all_client_data if c['days_remaining'] <= 14]
    
    filtered_client_data.sort(key=lambda x: (x['expired'], x['days_remaining']))

    return render_template(
        'dashboard.html',
        squid_status=squid_status_text,
        server_uptime=server_uptime,
        squid_started_time=squid_started_time,
        squid_reload_time=squid_reload_time,
        squid_port=squid_port,
        client_data=filtered_client_data,
        total_ips=total_ips,
        active_ips=active_ips,
        expired_ips=expired_ips,
        total_domains=total_domains,
        active_tab='dashboard'
    )

@dashboard_bp.route('/api/system_stats', methods=['GET'])
def system_stats():
    return SystemService.get_system_stats()

@dashboard_bp.route('/api/bandwidth_history', methods=['GET'])
def bandwidth_history():
    """API endpoint để lấy bandwidth history data cho chart."""
    hours = request.args.get('hours', default=24, type=int)
    chart_data = BandwidthHistoryService.get_chart_data(hours)
    return jsonify(chart_data)
