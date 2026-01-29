from app.extensions import db
from datetime import datetime


class DomainTemplate(db.Model):
    """
    Domain Template model for storing groups of domains.
    Used for quick template selection when configuring client whitelist.
    """
    __tablename__ = 'domain_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    domains = db.Column(db.Text, nullable=False)  # JSON string of domain list
    description = db.Column(db.String(255), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DomainTemplate {self.name}>'

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        import json
        return {
            'id': self.id,
            'name': self.name,
            'domains': json.loads(self.domains) if self.domains else [],
            'description': self.description or '',
            'date_created': self.date_created.strftime('%Y-%m-%d') if self.date_created else 'N/A',
            'date_modified': self.date_modified.strftime('%Y-%m-%d') if self.date_modified else 'N/A'
        }

    def get_domains_list(self):
        """Get domains as Python list."""
        import json
        try:
            return json.loads(self.domains) if self.domains else []
        except json.JSONDecodeError:
            return []

    def set_domains_list(self, domains_list):
        """Set domains from Python list."""
        import json
        self.domains = json.dumps(domains_list)
