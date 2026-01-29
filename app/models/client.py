from app import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False, unique=True)
    dns_hostname = db.Column(db.String(128), nullable=True)  # Thêm cột DNS or Hostname
    ticket_id = db.Column(db.String(50), nullable=True)  # Thêm cột Ticket ID
    expiration_date = db.Column(db.Date, nullable=False)
    allowed_domains = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())
    notes = db.Column(db.Text, nullable=True)

    def is_expired(self):
        return datetime.now().date() > self.expiration_date

    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'dns_hostname': self.dns_hostname,
            'ticket_id': self.ticket_id,
            'allowed_domains': self.allowed_domains,
            'expiration_date': self.expiration_date.strftime('%Y-%m-%d'),
            'notes': self.notes,
        }