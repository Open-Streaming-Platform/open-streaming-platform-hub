from typing import Union, Iterable
import requests, logging, datetime
from classes import servers
from classes.shared import db

log = logging.getLogger("app.functions.server_func")

def getServerAPI(serverId, endpoint):
    results = None
    server_query = servers.server.query.filter_by(id=serverId).first()
    if server_query is not None:
        try:
            r = requests.get(server_query.get_Url() + '/apiv1/' + endpoint, timeout=60)
            if r.status_code == 200:
                results = r.json()['results']
                server_query.serverActive = True
            else:
                server_query.serverActive = False
        except:
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
                server_query.serverImage = serverSettings['siteLogo']
                return_confirmation = True
            else:
                server_query.serverConfirmed = False
    db.session.commit()
    db.session.close()
    return return_confirmation

def checkServerOnline(serverId):
    results = False
    serverSettings = getServerAPI(serverId, 'server/ping')
    if serverSettings is not None:
        servers.server.query.filter_by(id=serverId).update(dict(serverLastUpdate=datetime.datetime.now()))
        db.session.commit()
        db.session.close()
        results = True
        verifyServer(serverId)
    return results

def getServerHubChannels(serverId):
    serverSettings = getServerAPI(serverId, 'channel/hubChannels')
    return serverSettings

def getServerLiveChannels(serverId):
    serverSettings = getServerAPI(serverId, 'channel/activeChannels')
    return serverSettings
    

def updateServer(serverId):
    log.info("Updating Topics for ServerId:" + str(serverId) )
    updateServerTopics(serverId)
    log.info("Updating Live Streams for ServerId:" + str(serverId) )
    updateServerLiveStreams(serverId)

def updateServerTopics(serverId):
    topics = getServerAPI(serverId, 'topic/')
    apiTopicIds = None
    parsed = {'new': [], 'updated': [], 'deleted': []}
    if topics is not None:
        apiTopicIds = []
        for topic in topics:
            apiTopicIds.append(topic['id'])
            topicQuery = servers.topic.query.filter_by(serverId=int(serverId), topicId=int(topic['id'])).first()
            if topicQuery is not None:
                topicQuery.name = topic['name']
                log.info('Updating Topic - ' + str(serverId) + ":" + " " + str(topic['id']) + "/" + topic['name'])
                db.session.commit()
                parsed['updated'].append(topic['id'])
            else:
                newTopic = servers.topic(int(serverId), topic['id'], topic['name'])
                db.session.add(newTopic)
                log.info('Adding New Topic - ' + str(serverId) + ":" + " " + str(topic['id']) + "/" + topic['name'])
                db.session.commit()
                parsed['new'].append(topic['id'])
        nonMatchingTopics = servers.topic.query.filter_by(serverId=int(serverId)).filter(~servers.topic.id.in_(apiTopicIds)).all()
        for item in nonMatchingTopics:
            log.info('Removing Non-Matching Topic - ' + str(serverId) + ":" + " " + str(item.id) + "/" + item.name)
            parsed['deleted'].append(item.id)
            db.session.delete(item)
        db.session.commit()
        db.session.close()
    return parsed

def formatQueryReturn(data):
    newArray = []
    for row in data:
        d = {}
        for column in row.__table__.columns:
            d[column.name] = str(getattr(row, column.name))
        newArray.append(d)
    return newArray

def updateServerLiveStreams(serverId):
    streams = getServerAPI(serverId, 'stream/')

def debugTopics(serverId):
    parsedTopics = updateServerTopics(serverId)
    topics = servers.topic.query.filter_by(serverId=int(serverId)).all()
    return topics