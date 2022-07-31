import requests
from classes import servers
from classes.shared import db



def getServerAPI(serverId, endpoint):
    results = None
    server_query = servers.server.query.filter_by(id=serverId).first()
    if server_query is not None:
        r=requests.get(server_query.get_Url() + '/apiv1/' + endpoint)
        if r.status_code == 200:
            results = r.json()['results']
            server_query.serverActive = True
        else:
            server_query.serverActive = False
    db.session.commit()
    db.session.close()
    return results

def verifyServer(serverId):
    return_confirmation = False
    serverSettings = getServerAPI(serverId, 'server/')
    if serverSettings != None:
        server_query = servers.server.query.filter_by(id=serverId).first()
        if server_query is not None:
            # Add check to verify current hub url and if active
            if 'hubURL' in serverSettings and 'hubEnabled' in serverSettings and serverSettings['hubEnabled'] is True:
                server_query.serverConfirmed = True
                server_query.serverName = serverSettings['siteName']
                return_confirmation = True
            else:
                server_query.serverConfirmed = False
    db.session.commit()
    db.session.close()
    return return_confirmation

def updateServer(serverId):
    updateServerTopics(serverId)
    updateServerLiveStreams(serverId)

def updateServerTopics(serverId):
    topics = getServerAPI(serverId, 'topic/')
    if topics is not None:
        serverTopicQuery = servers.topic.query.filter_by(serverId=serverId).all()
        apiTopicIds = []
        for topic in topics:
            apiTopicIds.append(topic.id)
            topicQuery = serverTopicQuery.filter_by(topicId=topic['id']).first()
            if topicQuery is not None:
                topicQuery.name = topic['name']
            else:
                newTopic = servers.topic(serverId, topic['id'], topic['name'])
                db.session.add(newTopic)
        nonMatchingTopics = serverTopicQuery.filter(~serverTopicQuery.id.in_(apiTopicIds)).all()
        for item in nonMatchingTopics:
            db.session.delete(item)
        db.session.commit()
        db.session.close()
    

def updateServerLiveStreams(serverId):
    streams = getServerAPI(serverId, 'stream/')