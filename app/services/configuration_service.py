import os
import shutil
import logging
from datetime import datetime, date
from flask import current_app
from app.models.client import Client

class ConfigurationService:
    @staticmethod
    def clear_directory(directory_path, exclude_file="default.conf"):
        """Delete all files in the directory except the specified file."""
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                try:
                    if filename == exclude_file:
                        continue
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path) # Recursively remove dirs if any
                except Exception as e:
                    logging.error(f"Error deleting {file_path}: {e}")



    @staticmethod
    def generate_config():
        """Generate Squid configuration files from DB."""
        try:
            output_dir = current_app.config.get('OUTPUT_DIR', 'output/')
            os.makedirs(output_dir, exist_ok=True)
            ConfigurationService.clear_directory(output_dir)

            valid_clients = Client.query.filter(Client.expiration_date >= date.today()).all()
            expired_clients = Client.query.filter(Client.expiration_date < date.today()).all()

            vip_ips = []
            vip_file_path = os.path.join(output_dir, 'VIP_clients.acl')

            for client in valid_clients:
                if client.allowed_domains.strip().upper() == "ANY":
                    vip_ips.append(client.ip_address)
                else:
                    ConfigurationService._generate_client_file(client, output_dir)

            if not vip_ips:
                vip_ips.append("127.0.0.2")

            with open(vip_file_path, 'w', encoding='utf-8') as vip_file:
                for ip in vip_ips:
                    vip_file.write(f"{ip}\n")

            # --- Global Whitelist Generation ---
            from app.models.whitelist import GlobalDomainWhitelist, GlobalIPWhitelist
            
            # 1. Global Domains List
            global_domains = GlobalDomainWhitelist.query.all()
            
            # Additional: Whitelist_domains.acl
            with open(os.path.join(output_dir, 'Whitelist_domains.acl'), 'w', encoding='utf-8') as f:
                for d in global_domains:
                    desc = f" # {d.description}" if d.description else ""
                    f.write(f"{d.domain}{desc}\n")
            
            # 2. Global IPs List
            global_ips = GlobalIPWhitelist.query.all()

            # Additional: Whitelist_ips.acl
            with open(os.path.join(output_dir, 'Whitelist_ips.acl'), 'w', encoding='utf-8') as f:
                for ip in global_ips:
                    desc = f" # {ip.description}" if ip.description else ""
                    f.write(f"{ip.ip_address}{desc}\n")
            


            return True, {
                'valid_count': len(valid_clients),
                'expired_count': len(expired_clients),
                'global_domains': len(global_domains),
                'global_ips': len(global_ips)
            }
        except Exception as e:
            logging.error(f"Error generating config: {e}")
            return False, str(e)

    @staticmethod
    def _generate_client_file(client, output_dir):
        ip = client.ip_address.replace('.', '_')
        if '/' in ip:
             ip = ip.replace('/', '-') # Handle CIDR
             
        exp_date = client.expiration_date.strftime('%Y%m%d')
        ip_filename = f"{ip}__{exp_date}_ip.conf"
        url_filename = f"{ip}__{exp_date}_url.conf"
        
        # IP Conf
        with open(os.path.join(output_dir, ip_filename), 'w') as f:
            f.write(
                f"acl client_{ip} src {client.ip_address}\n"
                f"acl allowed_sites_{ip} dstdomain \"/etc/squid/domains/{url_filename}\"\n"
                f"http_access allow client_{ip} CONNECT allowed_sites_{ip}\n"
                f"http_access allow client_{ip} allowed_sites_{ip}\n"
            )
        
        # URL Conf
        with open(os.path.join(output_dir, url_filename), 'w') as f:
            domains = client.allowed_domains.split('\n') if client.allowed_domains else []
            f.write('\n'.join(domains))

    @staticmethod
    def apply_config():
        """Apply generated config to Squid directories."""
        try:
            # Auto backup before applying
            from app.services.backup_service import BackupService
            BackupService.create_auto_backup()

            output_dir = current_app.config.get('OUTPUT_DIR')
            if not os.path.exists(output_dir):
                return False, "Output directory not found."

            squid_conf = current_app.config.get('SQUID_CONF_DIR')
            squid_domains = current_app.config.get('SQUID_DOMAINS_DIR')
            
            # Ensure dirs exist (mocking relative paths in Dev)
            os.makedirs(squid_conf, exist_ok=True)
            os.makedirs(squid_domains, exist_ok=True)
            
            ConfigurationService.clear_directory(squid_conf)
            ConfigurationService.clear_directory(squid_domains)

            vip_dir = '/etc/squid/VIP' if os.name != 'nt' else 'config/squid/VIP' 
            os.makedirs(vip_dir, exist_ok=True)

            # Track copied files
            copied_files = {'vip': 0, 'conf': 0, 'domains': 0}
            
            for filename in os.listdir(output_dir):
                src = os.path.join(output_dir, filename)
                if os.path.isfile(src):
                    if filename == 'VIP_clients.acl' or filename.startswith('Whitelist_'):
                        dest = os.path.join(vip_dir, filename)
                        shutil.copy(src, dest)
                        copied_files['vip'] += 1
                        logging.info(f"Copied {filename} to {dest}")
                    elif filename.endswith('_ip.conf'):
                        dest = os.path.join(squid_conf, filename)
                        shutil.copy(src, dest)
                        copied_files['conf'] += 1
                        logging.info(f"Copied {filename} to {dest}")
                    elif filename.endswith('_url.conf'):
                        dest = os.path.join(squid_domains, filename)
                        shutil.copy(src, dest)
                        copied_files['domains'] += 1
                        logging.info(f"Copied {filename} to {dest}")
            
            msg = (
                f"Configuration applied successfully!<br>"
                f"• VIP files: {copied_files['vip']}<br>"
                f"• Config files: {copied_files['conf']}<br>"
                f"• Domain files: {copied_files['domains']}<br>"
                f"• Squid Conf Dir: {squid_conf}<br>"
                f"• Squid Domains Dir: {squid_domains}<br>"
                f"• VIP Dir: {vip_dir}"
            )
            
            return True, msg
        except Exception as e:
            logging.error(f"Error applying config: {e}")
            return False, str(e)

    @staticmethod
    def reload_squid():
        """Reload Squid service."""
        if os.name == 'nt':
            logging.info("Windows Dev: Squid reload mocked.")
            return True, "Squid reloaded (Dev)."
        
        try:
            res = os.system('systemctl reload squid')
            if res == 0:
                return True, "Squid reloaded."
            return False, "Failed to reload Squid (exit code != 0)"
        except Exception as e:
            return False, str(e)
