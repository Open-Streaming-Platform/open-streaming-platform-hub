from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from celery import Celery

db = SQLAlchemy()
cache = Cache()
celery = Celery()