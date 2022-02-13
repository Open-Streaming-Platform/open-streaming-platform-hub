# -*- coding: UTF-8 -*-
# Flask Monkeypatch for Gevent
#from gevent import monkey
#monkey.patch_all(thread=True)

# Import Config
import config

# Import 3rd Party Libraries
from flask import Flask, redirect, request, abort, flash, current_app, session
from flask_migrate import Migrate, upgrade, init, migrate

# Modal Imports
from classes import servers
from classes import channels

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = config.dbLocation
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if config.dbLocation[:6] != "sqlite":
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

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)