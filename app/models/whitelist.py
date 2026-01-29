from app.extensions import db

class GlobalDomainWhitelist(db.Model):
    __tablename__ = 'global_domain_whitelist'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain,
            'description': self.description,
            'date_added': self.date_added.strftime('%Y-%m-%d') if self.date_added else 'N/A'
        }

class GlobalIPWhitelist(db.Model):
    __tablename__ = 'global_ip_whitelist'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'description': self.description,
            'date_added': self.date_added.strftime('%Y-%m-%d') if self.date_added else 'N/A'
        }
