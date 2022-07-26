import requests
from classes import servers
from classes.shared import db

def verifyServer(serverId):
    return_confirmation = False
    server_query = servers.server.query.filter_by(id=serverId).first()
    if server_query is not None:
        r=requests.get(server_query.get_Url)
        if r.status_code == 200:
            settings = r.json()['results']
            # Add check to verify current hub url and if 
            if 'hubURL' in settings and 'hubEnabled' in settings and settings['hubEnabled'] is True:
                server_query.serverConfirmed = True
                server_query.serverName = settings['siteName']
        else:
            server_query.serverConfirmed = False
            server_query.serverActive = False
    db.session.commit()
    db.session.close()
    return return_confirmation

