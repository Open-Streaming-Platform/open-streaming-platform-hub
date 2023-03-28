import datetime
from flask import request

from flask_restx import Api, Resource, reqparse, Namespace
from classes import channels, servers
from classes.shared import db

import functions

api = Namespace('channel', description='Channel Related Queries and Functions')

@api.route('/')
class api_server_root(Resource):
    def get(self):
        """
        Lists all attached channels
        """

        serversQuery = channels.channel.query.all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in serversQuery if ob.serverActive is True]}