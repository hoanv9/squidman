from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response
from app.services.whitelist_service import WhitelistService
from app.services.domain_template_service import DomainTemplateService
from flask_login import login_required
import json

whitelist_bp = Blueprint('whitelist', __name__)

@whitelist_bp.route('/whitelist', methods=['GET'])
@login_required
def manage_whitelist():
    domains = [d.to_dict() for d in WhitelistService.get_all_domains()]
    ips = [i.to_dict() for i in WhitelistService.get_all_ips()]
    templates = [t.to_dict() for t in DomainTemplateService.get_all_templates()]
    return render_template('whitelist.html', active_tab='whitelist', domains=domains, ips=ips, templates=templates)

# --- DOMAIN ROUTES ---
@whitelist_bp.route('/whitelist/domains/add', methods=['POST'])
@login_required
def add_domain():
    data = {
        'domain': request.form.get('domain'),
        'description': request.form.get('description')
    }
    if not data['domain']:
        flash('Domain is required.', 'error')
    else:
        success, msg = WhitelistService.add_domain(data)
        flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/domains/edit/<int:id>', methods=['POST'])
@login_required
def edit_domain(id):
    data = {
        'domain': request.form.get('domain'),
        'description': request.form.get('description')
    }
    success, msg = WhitelistService.update_domain(id, data)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/domains/delete/<int:id>', methods=['GET']) # Using GET for simple links, ideally POST/DELETE
@login_required
def delete_domain(id):
    success, msg = WhitelistService.delete_domain(id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/domains/delete-bulk', methods=['POST'])
@login_required
def delete_bulk_domains():
    ids = request.form.getlist('item_ids')
    if not ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    count = 0
    errors = 0
    for id_str in ids:
        try:
            success, _ = WhitelistService.delete_domain(int(id_str))
            if success:
                count += 1
            else:
                errors += 1
        except:
            errors += 1
            
    flash(f"Deleted {count} domains. {errors} failed.", 'success' if errors == 0 else 'warning')
    return redirect(url_for('whitelist.manage_whitelist'))

# --- IP ROUTES ---
@whitelist_bp.route('/whitelist/ips/add', methods=['POST'])
@login_required
def add_ip():
    data = {
        'ip_address': request.form.get('ip_address'),
        'description': request.form.get('description')
    }
    if not data['ip_address']:
        flash('IP Address is required.', 'error')
    else:
        success, msg = WhitelistService.add_ip(data)
        flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/ips/edit/<int:id>', methods=['POST'])
@login_required
def edit_ip(id):
    data = {
        'ip_address': request.form.get('ip_address'),
        'description': request.form.get('description')
    }
    success, msg = WhitelistService.update_ip(id, data)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/ips/delete/<int:id>', methods=['GET'])
@login_required
def delete_ip(id):
    success, msg = WhitelistService.delete_ip(id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/ips/delete-bulk', methods=['POST'])
@login_required
def delete_bulk_ips():
    ids = request.form.getlist('item_ids')
    if not ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    count = 0
    errors = 0
    for id_str in ids:
        try:
            success, _ = WhitelistService.delete_ip(int(id_str))
            if success:
                count += 1
            else:
                errors += 1
        except:
            errors += 1
            
    flash(f"Deleted {count} IPs. {errors} failed.", 'success' if errors == 0 else 'warning')
    return redirect(url_for('whitelist.manage_whitelist'))

# --- DOMAIN EXPORT/IMPORT ---
@whitelist_bp.route('/whitelist/domains/export', methods=['GET'])
@login_required
def export_domains():
    """Export all domains as text file (domain #description format)."""
    domains = WhitelistService.get_all_domains()
    lines = []
    for d in domains:
        if d.description:
            lines.append(f"{d.domain} #{d.description}")
        else:
            lines.append(d.domain)
    content = '\n'.join(lines)
    return Response(
        content,
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment; filename=global_domains.txt'}
    )

@whitelist_bp.route('/whitelist/domains/import', methods=['POST'])
@login_required
def import_domains():
    """Import domains from text file (domain #description format)."""
    if 'file' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    try:
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        success_count = 0
        skip_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse: domain #description
            if '#' in line:
                parts = line.split('#', 1)
                domain = parts[0].strip()
                description = parts[1].strip()
            else:
                domain = line
                description = ''
            
            data = {'domain': domain, 'description': description}
            success, msg = WhitelistService.add_domain(data)
            if success:
                success_count += 1
            else:
                skip_count += 1
        
        flash(f"Import completed! Added: {success_count}, Skipped: {skip_count}", 'success')
    except Exception as e:
        flash(f'Import failed: {str(e)}', 'error')
    
    return redirect(url_for('whitelist.manage_whitelist'))

# --- IP EXPORT/IMPORT ---
@whitelist_bp.route('/whitelist/ips/export', methods=['GET'])
@login_required
def export_ips():
    """Export all IPs as text file (ip #description format)."""
    ips = WhitelistService.get_all_ips()
    lines = []
    for ip in ips:
        if ip.description:
            lines.append(f"{ip.ip_address} #{ip.description}")
        else:
            lines.append(ip.ip_address)
    content = '\n'.join(lines)
    return Response(
        content,
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment; filename=global_ips.txt'}
    )

@whitelist_bp.route('/whitelist/ips/import', methods=['POST'])
@login_required
def import_ips():
    """Import IPs from text file (ip #description format)."""
    if 'file' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    try:
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        success_count = 0
        skip_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse: ip #description
            if '#' in line:
                parts = line.split('#', 1)
                ip_address = parts[0].strip()
                description = parts[1].strip()
            else:
                ip_address = line
                description = ''
            
            data = {'ip_address': ip_address, 'description': description}
            success, msg = WhitelistService.add_ip(data)
            if success:
                success_count += 1
            else:
                skip_count += 1
        
        flash(f"Import completed! Added: {success_count}, Skipped: {skip_count}", 'success')
    except Exception as e:
        flash(f'Import failed: {str(e)}', 'error')
    
    return redirect(url_for('whitelist.manage_whitelist'))

# --- DOMAIN TEMPLATE ROUTES ---
@whitelist_bp.route('/whitelist/templates/add', methods=['POST'])
@login_required
def add_template():
    data = {
        'name': request.form.get('name'),
        'domains': request.form.get('domains'),
        'description': request.form.get('description')
    }
    success, msg = DomainTemplateService.add_template(data)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/templates/edit/<int:id>', methods=['POST'])
@login_required
def edit_template(id):
    data = {
        'name': request.form.get('name'),
        'domains': request.form.get('domains'),
        'description': request.form.get('description')
    }
    success, msg = DomainTemplateService.update_template(id, data)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/templates/delete/<int:id>', methods=['GET'])
@login_required
def delete_template(id):
    success, msg = DomainTemplateService.delete_template(id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('whitelist.manage_whitelist'))

@whitelist_bp.route('/whitelist/templates/delete-bulk', methods=['POST'])
@login_required
def delete_bulk_templates():
    ids = request.form.getlist('item_ids')
    if not ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    count = 0
    errors = 0
    for id_str in ids:
        try:
            success, _ = DomainTemplateService.delete_template(int(id_str))
            if success:
                count += 1
            else:
                errors += 1
        except:
            errors += 1
            
    flash(f"Deleted {count} templates. {errors} failed.", 'success' if errors == 0 else 'warning')
    return redirect(url_for('whitelist.manage_whitelist'))

# --- TEMPLATE EXPORT ---
@whitelist_bp.route('/whitelist/templates/export', methods=['GET'])
@login_required
def export_templates():
    data = DomainTemplateService.export_to_json()
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    return Response(
        json_str,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=domain_templates.json'}
    )

# --- TEMPLATE IMPORT ---
@whitelist_bp.route('/whitelist/templates/import', methods=['POST'])
@login_required
def import_templates():
    if 'file' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    if not file.filename.endswith('.json'):
        flash('Only JSON files are allowed.', 'error')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    try:
        json_data = json.load(file)
        overwrite = request.form.get('overwrite') == 'on'
        success_count, skip_count, errors = DomainTemplateService.import_from_json(json_data, overwrite)
        
        if errors:
            flash(f"Import completed with errors: {', '.join(errors)}", 'warning')
        else:
            flash(f"Import successful! Added/Updated: {success_count}, Skipped: {skip_count}", 'success')
    except json.JSONDecodeError:
        flash('Invalid JSON file.', 'error')
    except Exception as e:
        flash(f'Import failed: {str(e)}', 'error')
    
    return redirect(url_for('whitelist.manage_whitelist'))

# --- API ENDPOINT (for client_manager.js) ---
@whitelist_bp.route('/api/templates', methods=['GET'])
@login_required
def api_get_templates():
    """API endpoint for fetching templates in format expected by client_manager.js"""
    data = DomainTemplateService.get_all_as_dict()
    return jsonify(data)


# --- MIGRATION: Import from static JSON file ---
@whitelist_bp.route('/whitelist/templates/migrate', methods=['GET'])
@login_required
def migrate_templates():
    """One-time migration: import templates from static JSON file to database."""
    import os
    
    json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'data', 'url_group.json')
    
    if not os.path.exists(json_path):
        flash('Source JSON file not found.', 'error')
        return redirect(url_for('whitelist.manage_whitelist'))
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        success_count, skip_count, errors = DomainTemplateService.import_from_json(json_data, overwrite=False)
        
        if errors:
            flash(f"Migration completed with errors: {', '.join(errors)}", 'warning')
        else:
            flash(f"Migration successful! Imported: {success_count}, Skipped (already exists): {skip_count}", 'success')
    
    except Exception as e:
        flash(f'Migration failed: {str(e)}', 'error')
    
    return redirect(url_for('whitelist.manage_whitelist'))

