import datetime
from flask import request

from flask_restx import Api, Resource, reqparse, Namespace
from classes import channels, servers
from classes.shared import db

from functions import server_func

api = Namespace('channel', description='Channel Related Queries and Functions')

@api.route('/')
class api_server_root(Resource):
    def get(self):
        """
        Lists all attached channels
        """

        channelQuery = channels.channel.query.all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in channelQuery]}
    
@api.route('/live')
class api_server_live(Resource):
    def get(self) -> dict:
        """
        Lists all Live Channels
        """
        channelQuery = (
            channels.channel.query
            .filter_by(channelLive=True)
            .join(servers.server, channels.channel.serverId == servers.server.id)
            .with_entities(
                servers.server.serverProtocol,
                servers.server.serverAddress,
                servers.server.serverName,
                servers.server.serverLastUpdate,
                channels.channel.channelLocation,
                channels.channel.channelImage,
                channels.channel.channelName,
                channels.channel.channelDescription,
                channels.channel.channelOwnerUsername,
                channels.channel.channelOwnerPicture,
                channels.channel.channelViewers,
                channels.channel.channelLastUpdated,
                channels.channel.channelNSFW
            )
            .all()
        )
        returnArray = []
        for chan in channelQuery:
            val = {
                "serverProtocol": chan.serverProtocol,
                "serverAddres": chan.serverAddress,
                "serverName": chan.serverName,
                "serverLastUpdate": str(chan.serverLastUpdate),
                "channelLocation": chan.channelLocation,
                "channelImage": chan.channelImage,
                "channelName": chan.channelName,
                "channelDescription": chan.channelDescription,
                "channelOwnerUsername": chan.channelOwnerUsername,
                "channelOwnerPicture": chan.channelOwnerPicture,
                "channelViewers": chan.channelViewers,
                "channelLastUpdated": str(chan.channelLastUpdated),
                "channelNSFW": chan.channelNSFW
            }
            returnArray.append(val)

        return {'results': returnArray}
