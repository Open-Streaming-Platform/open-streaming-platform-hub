# -*- coding: UTF-8 -*-
# Flask Monkeypatch for Gevent
#from gevent import monkey
#monkey.patch_all(thread=True)

import os, logging
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
dbLocation = os.getenv('OSP_HUB_DB')
debug = os.getenv('OSP_HUB_DEBUG')

if debug is None:
    debug = False

# Import 3rd Party Libraries
import sentry_sdk
from flask import Flask, redirect, request, abort, flash, current_app, session
from sentry_sdk.integrations.flask import FlaskIntegration
from flask.wrappers import Request
from flask_migrate import Migrate
from sqlalchemy import exc

# Sentry IO Config
sentry_sdk.init(
    dsn="https://60cdb6007a834f9cb0929c55a4f1bc6a@o996412.ingest.sentry.io/6630137",
    integrations=[
        FlaskIntegration(),
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

app.config['SQLALCHEMY_DATABASE_URI'] = dbLocation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if dbLocation[:6] != "sqlite":
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

# ----------------------------------------------------------------------------#
# Set Logging Configuration
# ----------------------------------------------------------------------------#
if __name__ != "__main__":
    loglevel = logging.WARNING
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
from blueprints.debug import debug_bp
from blueprints.api import api_v1

app.register_blueprint(root_bp)
app.register_blueprint(debug_bp)
app.register_blueprint(api_v1)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Initialize Flask-Caching
app.logger.info({"level": "info", "message": "Performing Flask Caching Initialization"})

from classes.shared import cache

redisHost = os.getenv('OSP_HUB_REDISHOST')
redisPort = os.getenv('OSP_HUB_REDISPORT')

if redisHost is not None and redisPort is not None:
    app.logger.info({"level": "info", "message": "Initializing Flask-Caching with Redis Backend"})
    redisCacheOptions = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_KEY_PREFIX": "OSP_HUB_FC",
        "CACHE_REDIS_HOST": redisHost,
        "CACHE_REDIS_PORT": redisPort,
    }
    if os.getenv('OSP_HUB_REDISPASSWORD') != "" and os.getenv('OSP_HUB_REDISPASSWORD') is not None:
        redisCacheOptions["CACHE_REDIS_PASSWORD"] = os.getenv('OSP_HUB_REDISPASSWORD')
    cache.init_app(app, config=redisCacheOptions)

else:
    app.logger.error({"level": "error", "message": "Flask-Caching Redis Configuration Missing.  Initializing as NullCache"})
    cacheOptions = {
        "CACHE_TYPE": "NullCache"
    }
    cache.init_app(app, config=cacheOptions)

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