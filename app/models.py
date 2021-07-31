from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    created_at = db.Column(db.DateTime())

    def __init__(self, email, password, date):
        self.email = email
        self.password = password
        self.created_at = date