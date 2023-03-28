import datetime
import requests

from .shared import db
import uuid

class channel(db.Model):
    __tablename__ = "channel"
    id = db.Column(db.Integer, primary_key=True)
    serverId = db.Column(db.Integer, db.ForeignKey('server.id'))
    channelName = db.Column(db.String(255))
    channelDescription = db.Column(db.String(2048))
    channelOwnerUsername = db.Column(db.String(256))
    channelOwnerPicture = db.Column(db.String(255))
    channelLocation = db.Column(db.String(255))
    channelViewers = db.Column(db.Integer)
    channelLive = db.Column(db.Boolean)
    channelLastUpdated = db.Column(db.DateTime)
    channelImage = db.Column(db.String(2048))

    def __init__(self, serverId, channelName, channelUsername, channelDescription, channelLocation, channelImage):
        self.serverId = serverId
        self.channelName = channelName
        self.channelOwnerUsername = channelUsername
        self.channelDescription = channelDescription
        self.channelLocation = channelLocation
        self.channelViewers = 0
        self.channelLive = False
        self.channelLastUpdated = datetime.datetime.now()
        self.channelImage = channelImage

    def update_info(self):
        try:
            r = requests.get(self.server.get_Url() + "/apiv1/channel/" + self.channelLocation, timeout=5.0)
        except requests.RequestException as e:
            self.server.serverActive = False
            db.session.commit()
            db.session.close()
            return False, {'message': 'error: ' + str(e) + '  - ' + self.server.id}

        if r.status_code != 200:
            self.server.serverActive = False
            db.session.commit()
            db.session.close()
            return False, {'message': 'error: Server Error ' + str(r.status_code) + ' - ' + self.server.id}
        else:
            returnedData = r.json()['results']
            if not (len(returnedData) > 0 and len(returnedData) < 2):
                return False, {'message': 'Error: Channel Location Invalid'}

            self.channelName = returnedData[0]['channelName']
            self.channelDescription = returnedData[0]['description']
            self.channelOwnerUsername = returnedData[0]['owningUsername']
            self.channelViewers = returnedData[0]['currentViews']
            self.channelLastUpdated = datetime.datetime.now()

            if len(returnedData[0]['stream']) > 0:
                self.channelLive = True
            else:
                self.channelLive = False

            if 'channelImage' in returnedData[0]:
                channelImage = returnedData[0]['channelImage']
                self.channelImage = channelImage
            db.session.commit()

            return True, {'message': 'Info: Channel Data Updated'}

    def serialize(self):
        return {
            'id': self.id,
            'serverId': self.serverId,
            'channelName': self.channelName,
            'channelDescription': self.channelDescription,
            'channelLocation': self.channelLocation,
            'channelViewers': self.channelViewers,
            'channelLive': self.channelLive,
            'channelLastUpdated': str(self.channelLastUpdated),
            'channelImage': self.channelImage,
        }