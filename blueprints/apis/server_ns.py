import datetime

from flask_restx import Api, Resource, reqparse, Namespace
from classes import servers
from classes.shared import db

api = Namespace('server', description='Server Related Queries and Functions')

serverAdd = reqparse.RequestParser()
serverAdd.add_argument('address', type=str, required=True, location=['args','form'])
serverAdd.add_argument('protocol', type=str, required=True, location=['args','form'])

serverDelete = reqparse.RequestParser()
serverDelete.add_argument('id', type=str, required=True, location=['args','form'])
serverDelete.add_argument('token', type=str, required=True, location=['args','form'])

@api.route('/')
@api.doc(params={'address': 'Full Domain of OSP Server', 'protocol':'HTTP or HTTPs', 'id': 'Server UUID', 'token': 'Server Auth Token'})
class api_server_root(Resource):
    def get(self):
        """
        Lists all attached Servers
        """

        serversQuery = servers.server.query.all()
        db.session.commit()
        return {'results': [ob.serialize() for ob in serversQuery if ob.serverActive is True]}

    @api.expect(serverAdd)
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def post(self):
        """
        Adds a Server to the OSP Hub
        """

        args = serverAdd.parse_args()

        if 'address' in args and 'protocol' in args:
            address = args['address']
            protocol = args['protocol']

            existingServerQuery = servers.server.query.filter_by(serverAddress=address).first()
            if existingServerQuery is not None:
                return {'results': {'success': False, 'message': 'Error: Duplicate Server Address'}}, 400

            if protocol != "http" and protocol != "https":
                return {'results': {'success': False, 'message': 'Error: Invalid Server Protocol'}}, 400

            newServer = servers.server(address, protocol)
            serverId = newServer.serverId
            token = newServer.serverToken
            db.session.add(newServer)
            db.session.commit()
            return {'results': {'success': True, 'message': 'Info: Server Added', 'serverUUID': str(serverId),
                                'token': str(token)}}, 200
        return {'results': {'success': False, 'message': 'Error: Missing Required Arguments'}}, 400

    @api.expect(serverDelete)
    @api.doc(responses={200: 'Success', 400: 'Request Error'})
    def delete(self):
        """
        Removes a Server from the OSP Hub
        """

        args = serverDelete.parse_args()

        if 'id' in args and 'token' in args:
            serverUUID = args['id'].lower()
            token = args['token'].lower()

            existingServerQuery = servers.server.query.filter_by(serverId=serverUUID, serverToken=token).first()
            if existingServerQuery is None:
                return {'results': {'success': False, 'message': 'Error: Invalid Server Address or Token'}}, 400

            db.session.delete(existingServerQuery)
            # TODO Remove Existing Channels or Streams

            db.session.commit()
            return {'results': {'success': True, 'message': 'Info: Server Removed', 'id': str(serverUUID)}}, 200
        return {'results': {'success': False, 'message': 'Error: Missing Required Arguments'}}, 400