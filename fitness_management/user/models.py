from ..database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False)
    last_name = db.Column(db.String(80), unique=False)
    role = db.Column(db.String(80), unique=False)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=False)
