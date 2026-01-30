from app.models.whitelist import GlobalDomainWhitelist, GlobalIPWhitelist
from app.extensions import db
from app.utils import is_valid_ip_or_cidr, validate_domain_entry
import logging

class WhitelistService:
    
    # --- DOMAIN OPERATIONS ---
    @staticmethod
    def get_all_domains():
        return GlobalDomainWhitelist.query.order_by(GlobalDomainWhitelist.domain).all()

    @staticmethod
    def add_domain(data):
        try:
            domain = data.get('domain')
            if not domain:
                return False, "Domain is required."
            
            # Use centralized validation
            if not validate_domain_entry(domain):
                return False, "Invalid domain format. Must be a valid domain (e.g., example.com) or subdomain (e.g., .google.com)."
            
            if GlobalDomainWhitelist.query.filter_by(domain=domain).first():
                return False, f"Domain {domain} already exists."
            
            new_domain = GlobalDomainWhitelist(
                domain=domain,
                description=data.get('description')
            )
            db.session.add(new_domain)
            db.session.commit()
            return True, f"Domain {domain} added successfully."
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding domain: {e}")
            return False, f"Error adding domain: {str(e)}"

    @staticmethod
    def delete_domain(domain_id):
        try:
            domain = GlobalDomainWhitelist.query.get(domain_id)
            if not domain:
                return False, "Domain not found."
            
            db.session.delete(domain)
            db.session.commit()
            return True, "Domain deleted."
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_domain(domain_id, data):
        try:
            domain_entry = GlobalDomainWhitelist.query.get(domain_id)
            if not domain_entry:
                return False, "Domain not found."
            
            new_domain = data.get('domain')
            if new_domain and new_domain != domain_entry.domain:
                if not validate_domain_entry(new_domain):
                     return False, "Invalid domain format. Must be a valid domain."
                if GlobalDomainWhitelist.query.filter_by(domain=new_domain).first():
                    return False, f"Domain {new_domain} already exists."
                domain_entry.domain = new_domain

            domain_entry.description = data.get('description', domain_entry.description)
            db.session.commit()
            return True, "Domain updated."
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    # --- IP OPERATIONS ---
    @staticmethod
    def get_all_ips():
        return GlobalIPWhitelist.query.order_by(GlobalIPWhitelist.ip_address).all()

    @staticmethod
    def add_ip(data):
        try:
            ip = data.get('ip_address')
            if not ip:
                return False, "IP Address is required."
            if not is_valid_ip_or_cidr(ip):
                return False, "Invalid IP address or CIDR format (e.g., 192.168.1.1 or 192.168.1.0/24)."

            if GlobalIPWhitelist.query.filter_by(ip_address=ip).first():
                return False, f"IP {ip} already exists."
            
            new_ip = GlobalIPWhitelist(
                ip_address=ip,
                description=data.get('description')
            )
            db.session.add(new_ip)
            db.session.commit()
            return True, f"IP {ip} added successfully."
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding IP: {e}")
            return False, f"Error adding IP: {str(e)}"

    @staticmethod
    def delete_ip(ip_id):
        try:
            ip = GlobalIPWhitelist.query.get(ip_id)
            if not ip:
                return False, "IP not found."
            
            db.session.delete(ip)
            db.session.commit()
            return True, "IP deleted."
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_ip(ip_id, data):
        try:
            ip_entry = GlobalIPWhitelist.query.get(ip_id)
            if not ip_entry:
                return False, "IP not found."
            
            new_ip = data.get('ip_address')
            if new_ip and new_ip != ip_entry.ip_address:
                if not is_valid_ip_or_cidr(new_ip):
                    return False, "Invalid IP address or CIDR format (e.g., 192.168.1.1 or 192.168.1.0/24)."
                if GlobalIPWhitelist.query.filter_by(ip_address=new_ip).first():
                     return False, f"IP {new_ip} already exists."
                ip_entry.ip_address = new_ip

            ip_entry.description = data.get('description', ip_entry.description)
            db.session.commit()
            return True, "IP updated."
        except Exception as e:
            db.session.rollback()
            return False, str(e)
