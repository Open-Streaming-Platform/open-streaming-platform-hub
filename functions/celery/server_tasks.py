from celery.canvas import subtask
from celery.result import AsyncResult

import datetime
import logging

from classes import servers, channels
from functions import server_func

from classes.shared import celery, db

log = logging.getLogger("app.functions.celery.scheduler.channel_tasks")


def setup_server_tasks(sender, **kwargs):
    sender.add_periodic_task(300, verify_servers.s(), name='Validate Unconfirmed Servers')
    sender.add_periodic_task(240, check_servers_heartbeat.s(), name='Check Servers Online')
    sender.add_periodic_task(280, check_servers_hub_channels.s(), name='Get Server Channels')
    return True

@celery.task(bind=True)
def verify_servers(self):
    serverQuery = servers.server.query.filter_by(serverConfirmed=False).with_entities(servers.server.id).all()
    for server in serverQuery:
        results = subtask("functions.celery.server_tasks.verify_server", args=(server.id,)).apply_async()
    return True

@celery.task(bind=True)
def verify_server(self, serverId):
    server_func.verifyServer(serverId)
    return True

@celery.task(bind=True)
def check_servers_heartbeat(self):
    serverQuery = servers.server.query.filter_by(serverConfirmed=True).with_entities(servers.server.id).all()
    for server in serverQuery:
        results = subtask("functions.celery.server_tasks.check_server_heartbeat", args=(server.id,)).apply_async()
    return True

@celery.task(bind=True)
def check_server_heartbeat(self, serverId):
    server_func.checkServerOnline(serverId)
    return True

@celery.task(bind=True)
def check_servers_hub_channels(self):
    serverQuery = servers.server.query.filter_by(serverConfirmed=True, serverActive=True).with_entities(servers.server.id).all()
    for server in serverQuery:
        results = subtask("functions.celery.server_tasks.check_server_hub_channels", args=(server.id,)).apply_async()
    return True

@celery.task(bind=True)
def check_server_hub_channels(self, serverId):
    results = server_func.getServerHubChannels(serverId)
    # Iterate over for Existing Channels
    returnedIds = []
    existingIds = [x.channelLocation for x in channels.channel.query.filter_by(serverId=serverId).with_entities(channels.channel.channelLocation).all()]

    for result in results:
        returnedIds.append(result['channelEndpointID'])
        
        isLive = False
        if len(result['stream']) > 0:
            isLive = True

        existingChannel = channels.channel.query.filter_by(serverId=serverId, channelLocation=result['channelEndpointID']).with_entities(channels.channel.id).first()
        if existingChannel is None:
            newChan = (
                channels.channel(serverId, result['channelName'], result['owningUsername'], result['description'], result['channelEndpointID'], result['channelImage'], isLive))
            db.session.add(newChan)
        else:
            channels.channel.query.filter_by(id=existingChannel.id).update(dict(
                    serverId = serverId,
                    channelName = result['channelName'],
                    channelDescription =  result['description'],
                    channelOwnerUsername = result['owningUsername'],
                    channelOwnerPicture = result['owningUserImage'],
                    channelLocation = result['channelEndpointID'],
                    channelViewers = result['currentViews'],
                    channelLive = isLive,
                    channelLastUpdated = datetime.datetime.now(),
                    channelImage = result['channelImage'],
                    channelNSFW = result['hubNSFW']
            ))
    for existing in existingIds:
        if existing not in returnedIds:
            channels.channel.query.filter_by(channelLocation=existing).delete()
    db.session.commit()
    return True  