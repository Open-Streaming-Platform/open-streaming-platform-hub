# -*- coding: UTF-8 -*-
# Flask Monkeypatch for Gevent
#from gevent import monkey
#monkey.patch_all(thread=True)

import os, logging
from dotenv import load_dotenv

# Load Environment Variables
class configObj:
        pass

load_dotenv()
config = configObj()
config.dbLocation = os.getenv('OSP_HUB_DB')
config.debug = os.getenv('OSP_HUB_DEBUG')
config.redisHost = os.getenv("OSP_REDIS_HOST")
config.redisPort = os.getenv("OSP_REDIS_PORT")
config.redisPassword = os.getenv("OSP_REDIS_PASSWORD")

if config.debug is None:
    debug = False

# Import 3rd Party Libraries
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import redis
from flask import Flask, redirect, request, abort, flash, current_app, session
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration
from flask.wrappers import Request
from flask_migrate import Migrate
from sqlalchemy import exc

# Initialize RedisURL Variable
RedisURL = None
if config.redisPassword == "" or config.redisPassword is None:
    RedisURL = "redis://" + config.redisHost + ":" + str(config.redisPort)
else:
    RedisURL = (
        "redis://:"
        + config.redisPassword
        + "@"
        + config.redisHost
        + ":"
        + str(config.redisPort)
    )


# Sentry IO Config
sentry_sdk.init(
    dsn="https://60cdb6007a834f9cb0929c55a4f1bc6a@o996412.ingest.sentry.io/6630137",
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

# Modal Imports
from classes import servers
from classes import channels
from classes import secrets

app = Flask(__name__)

app.config["broker_url"] = RedisURL
app.config["result_backend"] = RedisURL
app.config['SQLALCHEMY_DATABASE_URI'] = config.dbLocation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if config.dbLocation[:6] != "sqlite":
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = -1
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 300
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 600
    app.config['MYSQL_DATABASE_CHARSET'] = "utf8"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'encoding': 'utf8', 'pool_use_lifo': 'False', 'pool_size': 10, "pool_pre_ping": True}

# ----------------------------------------------------------------------------#
# Monkey Fix Flask-Restx issue (https://github.com/pallets/flask/issues/4552#issuecomment-1109785314)
# ----------------------------------------------------------------------------#
class AnyJsonRequest(Request):
    def on_json_loading_failed(self, e):
        if e is not None:
            return super().on_json_loading_failed(e)

app.request_class = AnyJsonRequest

# Enable CORS
CORS(app)

# ----------------------------------------------------------------------------#
# Set Logging Configuration
# ----------------------------------------------------------------------------#
if __name__ != "__main__":
    loglevel = logging.INFO
    configLogLevel = os.getenv('OSP_HUB_LOGLEVEL')
    if configLogLevel != None:
        logOptions = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        if configLogLevel.lower() in logOptions:
            loglevel = logOptions[configLogLevel.lower()]
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(loglevel)

# Begin Database Initialization
from classes.shared import db
db.init_app(app)
db.app = app

migrate = Migrate(app, db)

# Handle Session Rollback Issues
@app.errorhandler(exc.SQLAlchemyError)
def handle_db_exceptions(error):
    app.logger.error(error)
    db.session.rollback()

# Import Blueprints
from blueprints.pages import root_bp
from blueprints.api import api_v1

app.register_blueprint(root_bp)
app.register_blueprint(api_v1)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Initialize Redis
app.logger.info({"level": "info", "message": "Initializing Redis"})
if config.redisPassword == "" or config.redisPassword is None:
    r = redis.Redis(host=config.redisHost, port=config.redisPort)
    app.config["SESSION_REDIS"] = r
else:
    r = redis.Redis(
        host=config.redisHost, port=config.redisPort, password=config.redisPassword
    )
    app.config["SESSION_REDIS"] = r
r.flushdb()

# Initialize Flask-Caching
app.logger.info({"level": "info", "message": "Performing Flask Caching Initialization"})

from classes.shared import cache

redisHost = os.getenv('OSP_REDIS_HOST')
redisPort = os.getenv('OSP_REDIS_PORT')

if redisHost is not None and redisPort is not None:
    app.logger.info({"level": "info", "message": "Initializing Flask-Caching with Redis Backend"})
    redisCacheOptions = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_KEY_PREFIX": "OSP_HUB_FC",
        "CACHE_REDIS_HOST": redisHost,
        "CACHE_REDIS_PORT": redisPort,
    }
    if os.getenv('OSP_REDIS_PASSWORD') != "" and os.getenv('OSP_REDIS_PASSWORD') is not None:
        redisCacheOptions["CACHE_REDIS_PASSWORD"] = os.getenv('OSP_REDIS_PASSWORD')
    cache.init_app(app, config=redisCacheOptions)

else:
    app.logger.error({"level": "error", "message": "Flask-Caching Redis Configuration Missing.  Initializing as NullCache"})
    cacheOptions = {
        "CACHE_TYPE": "NullCache"
    }
    cache.init_app(app, config=cacheOptions)

# Initialize Celery
app.logger.info({"level": "info", "message": "Initializing Celery"})
from classes.shared import celery

celery.conf.broker_url = app.config["broker_url"]
celery.conf.result_backend = app.config["result_backend"]
celery.conf.update(app.config)

class ContextTask(celery.Task):
    """Make celery tasks work with Flask app context"""

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

# Import Celery Beat Scheduled Tasks
from functions.celery import scheduler

# Generate Initial API Key
try:
    apiKeyQuery = secrets.apikey.query.first()
    if apiKeyQuery is None:
        newApiKey = secrets.apikey()
        db.session.add(newApiKey)
        print('Initial OSP Hub API Key: ' + newApiKey.apikey)
    db.session.commit()
except:
    print("No DB Schema Exists")


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=debug)