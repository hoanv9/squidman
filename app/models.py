from app import db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)  # Đảm bảo IP là duy nhất
    expiration_date = db.Column(db.Date, nullable=False)
    allowed_domains = db.Column(db.PickleType, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)