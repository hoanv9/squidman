from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from app.services.configuration_service import ConfigurationService
from app.services.backup_service import BackupService
from app.services.system_service import SystemService

configuration_bp = Blueprint('apply_configuration', __name__)

@configuration_bp.route('/apply_configuration', methods=['GET', 'POST'])
@login_required
def apply_configuration():
    # Configure logging context if needed, but Service has its own logging.
    # The original code re-configured basicConfig here, which is weird. 
    # Global logging config should be in __init__.py or dedicated logging setup.
    # We'll skip re-configuring logging here to avoid side effects.

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'generate_config':
            success, result = ConfigurationService.generate_config()
            if success:
                msg = (
                    f"Configuration generated successfully!<br>"
                    f"• Valid Clients: <strong>{result['valid_count']}</strong><br>"
                    f"• Expired Clients: <strong>{result['expired_count']}</strong><br>"
                    f"• Global Domains: <strong>{result['global_domains']}</strong><br>"
                    f"• Global IPs: <strong>{result['global_ips']}</strong>"
                )
                flash(msg, 'success')
            else:
                flash(f"Error generating configuration: {result}", 'error')
        
        elif action == 'apply_config':
            success, msg = ConfigurationService.apply_config()
            flash(msg, 'success' if success else 'error')
            
        elif action == 'reload_squid':
            success, msg = ConfigurationService.reload_squid()
            flash(msg, 'success' if success else 'error')
            

        elif action == 'one_click_apply':
            try:
                s1, m1 = ConfigurationService.generate_config()
                if not s1: raise Exception(m1)
                
                s2, m2 = ConfigurationService.apply_config()
                if not s2: raise Exception(m2)
                
                s3, m3 = ConfigurationService.reload_squid()
                if not s3: raise Exception(m3)
                
                
                msg = (
                    f"<strong>1-Click Apply Completed!</strong><br>"
                    f"• Generated: {m1['valid_count']} valid, {m1['expired_count']} expired<br>"
                    f"• Global: {m1['global_domains']} domains, {m1['global_ips']} IPs<br>"
                    f"• Status: Applied & Reloaded"
                )
                flash(msg, 'success')
            except Exception as e:
                flash(f'Error during 1-Click Apply: {e}', 'error')

        return redirect(url_for('apply_configuration.apply_configuration'))

    # Get Squid port for Client Config display
    squid_port = SystemService.get_squid_port()
    
    return render_template('apply_configuration.html', active_tab='apply_configuration', squid_port=squid_port)

@configuration_bp.route('/backup/create', methods=['POST'])
@login_required
def create_manual_backup():
    """API tạo manual backup."""
    success, result = BackupService.create_manual_backup()
    flash(f"Backup created: {result}" if success else f"Backup failed: {result}", 'success' if success else 'error')
    return redirect(url_for('apply_configuration.apply_configuration'))

@configuration_bp.route('/backup/list', methods=['GET'])
@login_required
def list_backups():
    """API lấy danh sách backups."""
    backups = BackupService.list_backups()
    return jsonify(backups)

@configuration_bp.route('/backup/delete/<filename>', methods=['POST'])
@login_required
def delete_backup(filename):
    """API xóa backup."""
    success, msg = BackupService.delete_backup(filename)
    return jsonify({'success': success, 'message': msg})

@configuration_bp.route('/backup/restore/<filename>', methods=['POST'])
@login_required
def restore_backup(filename):
    """API restore backup."""
    success, msg = BackupService.restore_backup(filename)
    return jsonify({'success': success, 'message': msg})
