from celery.canvas import subtask
from celery.result import AsyncResult

import datetime
import logging

from classes import servers
from functions import server_func

from classes.shared import celery, db

log = logging.getLogger("app.functions.celery.scheduler.channel_tasks")


def setup_server_tasks(sender, **kwargs):
    sender.add_periodic_task(120, verify_servers.s(), name='Validate Unconfirmed Servers')
    pass

@celery.task(bind=True)
def verify_servers(self):
    serverQuery = servers.server.query.filter_by(serverConfirmed=False).all()
    for server in serverQuery:
        results = subtask("functions.celery.server_tasks.verify_server", args=(server.id))
    pass

@celery.task(bind=True)
def verify_server(serverId):
    server_func.verifyServer(serverId)