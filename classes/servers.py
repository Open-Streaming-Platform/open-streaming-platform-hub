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
    serverPort = db.Column(db.Integer)
    serverActive = db.Column(db.Boolean)
    serverLastUpdate = db.Column(db.DateTime)
    serverName = db.Column(db.String(255))
    serverToken = db.Column(db.String(512), unique=True)
    channels = db.relationship('channel', backref='server', cascade="all, delete-orphan", lazy="joined")

    def __init__(self, serverAddress, serverProtocol, serverPort):
        self.serverId = str(uuid.uuid4())
        self.serverAddress = serverAddress
        self.serverProtocol = serverProtocol
        self.serverPort = serverPort
        self.serverActive = True
        self.serverToken = secrets.token_hex(32)
        self.serverLastUpdate = datetime.datetime.now()

    def get_Url(self):
        fullUrl = None
        if (self.serverProtocol == "http" and self.serverPort == 80) or (self.serverProtocol == "https" and self.serverPort == 443):
            fullUrl = self.serverProtocol + "://" + self.serverAddress + "/"
        else:
            fullUrl = self.serverProtocol + "://" + self.serverAddress + ":" + self.serverPort + "/"
        return fullUrl

    def serialize(self):
        return {
            'id': self.id,
            'serverId': self.serverId,
            'serverAddress': self.serverAddress,
            'serverProtocol': self.serverProtocol,
            'serverPort': str(self.serverPort),
            'serverActive': self.serverActive,
            'serverLastUpdate': self.serverLastUpdate,
            'serverName': self.serverName,
        }