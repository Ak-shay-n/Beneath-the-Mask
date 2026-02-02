from . import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    teamname = db.Column(db.String(100))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)  # When user registered
    ispassword = db.Column(db.Boolean)
    passwordtime = db.Column(db.String(100))
    issecurityquestion = db.Column(db.Boolean)
    securitytime = db.Column(db.String(100))
    isofa = db.Column(db.Boolean)
    ofatime = db.Column(db.String(100))  # Time for Stage 3 (2FA/Date)
    completed = db.Column(db.String(100))
