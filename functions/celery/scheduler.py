import logging
from celery.schedules import crontab
from classes.shared import celery

from functions.celery import server_tasks

from datetime import timedelta

log = logging.getLogger("app.functions.scheduler")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Sets up Scheduled Tasks to be handled by Celery Beat
    """
    server_tasks.setup_server_tasks(sender, **kwargs)
