import datetime
import secrets

from .shared import db
import uuid

class server(db.Model):
    __tablename__ = "server"
    id = db.Column(db.Integer, primary_key=True)
    serverId = db.Column(db.String(255), unique=True)
    serverAddress = db.Column(db.String(255), unique=True)
    serverProtocol = db.Column(db.String(5))
    serverActive = db.Column(db.Boolean)
    serverLastUpdate = db.Column(db.DateTime)
    serverName = db.Column(db.String(255))
    serverToken = db.Column(db.String(512), unique=True)
    channels = db.relationship('channel', backref='server', cascade="all, delete-orphan", lazy="joined")

    def __init__(self, serverAddress, serverProtocol):
        self.serverId = str(uuid.uuid4())
        self.serverAddress = serverAddress
        self.serverProtocol = serverProtocol
        self.serverActive = True
        self.serverToken = secrets.token_hex(32)
        self.serverLastUpdate = datetime.datetime.now()

    def get_Url(self):
        fullUrl = self.serverProtocol + "://" + self.serverAddress + "/"
        return fullUrl

    def serialize(self):
        return {
            'id': self.id,
            'serverId': self.serverId,
            'serverAddress': self.serverAddress,
            'serverProtocol': self.serverProtocol,
            'serverActive': self.serverActive,
            'serverLastUpdate': str(self.serverLastUpdate),
            'serverName': self.serverName
        }