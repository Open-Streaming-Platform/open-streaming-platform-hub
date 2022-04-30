import secrets

from .shared import db
import uuid

class apikey(db.Model):
    __tablename__ = "apikey"
    id = db.Column(db.Integer, primary_key=True)
    apikey = db.Column(db.String(128))

    def __init__(self):
        self.apikey = secrets.token_hex(32)
