# -*- coding: UTF-8 -*-
# Flask Monkeypatch for Gevent
#from gevent import monkey
#monkey.patch_all(thread=True)

import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
dbLocation = os.getenv('OSP_HUB_DB')
debug = os.getenv('OSP_HUB_DEBUG')

if debug is None:
    debug = False

# Import 3rd Party Libraries
from flask import Flask, redirect, request, abort, flash, current_app, session

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
else:
    pass

# Begin Database Initialization
from classes.shared import db
db.init_app(app)
db.app = app

db.create_all()

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

# Generate Initial API Key
apiKeyQuery = secrets.apikey.query.first()
if apiKeyQuery is None:
    newApiKey = secrets.apikey()
    db.session.add(newApiKey)
    print('Initial OSP Hub API Key: ' + newApiKey.apikey)
db.session.commit()

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=debug)