from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.services.client_service import ClientService
from flask_login import login_required
from datetime import datetime

clients_bp = Blueprint('manage_clients', __name__)

@clients_bp.route('/clients', methods=['GET'])
@login_required
def manage_clients():
    clients = ClientService.get_all_clients()

    client_data = [
        {
            'id': client.id,
            'ip_address': client.ip_address,
            'dns_hostname': client.dns_hostname,
            'ticket_id': client.ticket_id,
            'notes': client.notes,
            'date_added': client.date_added.strftime('%d-%m-%Y'), # Display
            'date_added_iso': client.date_added.strftime('%Y-%m-%d'), # Sorting/Data
            'expiration_date': client.expiration_date.strftime('%d-%m-%Y'), # Display
            'expiration_date_iso': client.expiration_date.strftime('%Y-%m-%d'), # Sorting/Data
            'allowed_domains': client.allowed_domains.split('\n') if client.allowed_domains else [],
            'days_remaining': (client.expiration_date - datetime.now().date()).days,
            'expired': (client.expiration_date - datetime.now().date()).days < 0
        }
        for client in clients
    ]

    return render_template('manage_clients.html', active_tab='manage_clients', client_data=client_data)

@clients_bp.route('/clients/add', methods=['POST'])
@login_required
def add_client():
    data = {
        'ip_address': request.form.get('ip_address'),
        'dns_hostname': request.form.get('dns_hostname'),
        'ticket_id': request.form.get('ticket_id'),
        'expiration_date': request.form.get('expiration_date'),
        'allowed_domains': request.form.get('allowed_domains'),
        'notes': request.form.get('notes')
    }

    if not data['ip_address'] or not data['expiration_date']:
        flash('IP Address and Expiration Date are required.', 'error')
        return redirect(url_for('manage_clients.manage_clients'))

    success, message = ClientService.add_client(data)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('manage_clients.manage_clients'))

@clients_bp.route('/clients/edit/<int:client_id>', methods=['POST'])
@login_required
def edit_client(client_id):
    data = {
        'expiration_date': request.form.get('expiration_date'),
        'allowed_domains': request.form.get('allowed_domains'),
        'dns_hostname': request.form.get('dns_hostname'),
        'ticket_id': request.form.get('ticket_id'),
        'notes': request.form.get('notes')
    }

    if not data['expiration_date']:
        flash('Expiration Date is required.', 'error')
        return redirect(url_for('manage_clients.manage_clients'))

    success, message = ClientService.update_client(client_id, data)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('manage_clients.manage_clients'))

@clients_bp.route('/clients/delete/<int:client_id>', methods=['GET'])
@login_required
def delete_client(client_id):
    success, message = ClientService.delete_client(client_id)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('manage_clients.manage_clients'))

@clients_bp.route('/clients/delete_clients', methods=['POST'])
@login_required
def delete_clients():
    selected_clients = request.form.getlist('selected_clients')
    if not selected_clients:
        flash('Invalid client selection.', 'error')
        return redirect(url_for('manage_clients.manage_clients'))

    success, result = ClientService.delete_clients_bulk(selected_clients)
    if success:
        if result:
            flash(f'Deleted clients with IPs: {", ".join(result)}', 'success')
        else:
            flash('No clients were deleted.', 'info')
    else:
        flash(f'Error deleting clients: {result}', 'error')

    return redirect(url_for('manage_clients.manage_clients'))

@clients_bp.route('/api/nslookup', methods=['GET'])
@login_required
def nslookup():
    ip = request.args.get('ip')
    hostname, error = ClientService.perform_nslookup(ip)
    
    if error:
        return jsonify({'error': error, 'hostname': None}), 404 if "found" in error else 500
    return jsonify({'hostname': hostname})
