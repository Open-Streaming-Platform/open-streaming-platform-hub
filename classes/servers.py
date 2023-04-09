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
    serverConfirmed = db.Column(db.Boolean)
    serverLastUpdate = db.Column(db.DateTime)
    serverName = db.Column(db.String(255))
    serverToken = db.Column(db.String(512), unique=True)
    channels = db.relationship('channel', backref='server', cascade="all, delete-orphan", lazy="noload")
    topics = db.relationship('topic', backref='server', cascade="all, delete-orphan", lazy="noload")

    def __init__(self, serverAddress, serverProtocol):
        self.serverId = str(uuid.uuid4())
        self.serverAddress = serverAddress
        self.serverProtocol = serverProtocol
        self.serverActive = True
        self.serverConfirmed = False
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
            'serverConfirmed': self.serverConfirmed,
            'serverLastUpdate': str(self.serverLastUpdate),
            'serverName': self.serverName
        }

class topic(db.Model):
    __tablename__ = "topic"
    id = db.Column(db.Integer, primary_key=True)
    serverId = db.Column(db.Integer, db.ForeignKey('server.id'))
    topicId = db.Column(db.Integer)
    name = db.Column(db.String(255))
    
    def __init__(self, serverId, topicId, name):
        self.serverId = serverId
        self.topicId = topicId
        self.name = name


class stream(db.Model):
    __tablename__ = "stream"
    id = db.Column(db.Integer, primary_key=True)
    serverId = db.Column(db.String(255))
    serverChannelLoc = db.Column(db.String(255))
    streamerId = db.Column(db.Integer)
    streamPage = db.Column(db.String(255))
    streamName = db.Column(db.String(1024))
    thumbnail = db.Column(db.String(1024))
    gifThumbnail = db.Column(db.String(1024))
    topic = db.Column(db.Integer)
    
    def __init__(self, serverId, channelLoc, streamerId, streamPage, streamName, thumbnail, gifThumbnail, topics):
        self.serverId = serverId
        self.serverChannelLoc = channelLoc
        self.streamerId = streamerId
        self.streamPage = streamPage
        self.streamName = streamName
        self.thumbnail = thumbnail
        self.gifThumbnail = gifThumbnail
        self.topic = topics
        