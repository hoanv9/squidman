from app.models.client import Client
from app import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.utils import validate_allowed_domains
import dns.resolver
from flask import current_app

class ClientService:
    @staticmethod
    def get_all_clients():
        return Client.query.all()

    @staticmethod
    def get_client_by_id(client_id):
        return Client.query.get_or_404(client_id)

    @staticmethod
    def add_client(data):
        """
        Add a new client.
        data: dict containing ip_address, expiration_date, allowed_domains, etc.
        Returns: (success: bool, message: str)
        """
        try:
            allowed_domains_str = ''
            if data.get('allowed_domains'):
                unique_domains = validate_allowed_domains(data.get('allowed_domains'))
                allowed_domains_str = '\n'.join(unique_domains)

            # Auto-lookup hostname if not provided
            dns_hostname = data.get('dns_hostname')
            if not dns_hostname or dns_hostname.strip() == '':
                hostname, error = ClientService.perform_nslookup(data['ip_address'])
                if hostname and not error:
                    dns_hostname = hostname
                # If lookup fails, dns_hostname remains None/empty

            new_client = Client(
                ip_address=data['ip_address'],
                dns_hostname=dns_hostname,
                ticket_id=data.get('ticket_id'),
                expiration_date=datetime.strptime(data['expiration_date'], '%Y-%m-%d'),
                allowed_domains=allowed_domains_str,
                notes=data.get('notes'),
                date_added=datetime.utcnow()
            )
            
            db.session.add(new_client)
            db.session.commit()
            return True, "Client added successfully."
        except ValueError as e:
            return False, str(e)
        except IntegrityError:
            db.session.rollback()
            return False, f'IP Address "{data["ip_address"]}" already exists.'
        except Exception as e:
            db.session.rollback()
            return False, f'Error adding client: {e}'

    @staticmethod
    def update_client(client_id, data):
        client = ClientService.get_client_by_id(client_id)
        try:
            if data.get('allowed_domains'):
                unique_domains = validate_allowed_domains(data.get('allowed_domains'))
                client.allowed_domains = '\n'.join(unique_domains)
            else:
                client.allowed_domains = ''
            
            client.expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d')
            client.dns_hostname = data.get('dns_hostname')
            client.ticket_id = data.get('ticket_id')
            client.notes = data.get('notes')

            db.session.commit()
            return True, "Client updated successfully."
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            db.session.rollback()
            return False, f'Error updating client: {e}'

    @staticmethod
    def delete_client(client_id):
        client = ClientService.get_client_by_id(client_id)
        try:
            db.session.delete(client)
            db.session.commit()
            return True, "Client deleted successfully."
        except Exception as e:
            db.session.rollback()
            return False, f"Error deleting client: {e}"

    @staticmethod
    def delete_clients_bulk(client_ids):
        try:
            # Get IPs for logging
            clients_to_delete = Client.query.filter(Client.id.in_(client_ids)).all()
            deleted_ips = [client.ip_address for client in clients_to_delete]

            Client.query.filter(Client.id.in_(client_ids)).delete(synchronize_session=False)
            db.session.commit()
            return True, deleted_ips
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def perform_nslookup(ip):
        if not ip:
            return None, "IP address is required"
        
        dns_server = current_app.config.get('DNS_SERVER', '8.8.8.8')
        
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            answer = resolver.resolve_address(ip)
            return str(answer[0]), None
        except dns.resolver.NXDOMAIN:
            return None, "Hostname not found"
        except Exception as e:
            return None, str(e)
