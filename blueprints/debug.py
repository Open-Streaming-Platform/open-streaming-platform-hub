from flask import Blueprint, request, url_for, render_template, redirect, flash
from classes import servers, channels
from functions import server_func

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/servers')
def servers_debug():
    serverQuery = servers.server.query.all()
    return {'results': [ob.serialize() for ob in serverQuery]}

@debug_bp.route('/servers/<id>/confirm')
def servers_confirm_debug(id):
    results = server_func.verifyServer(id)
    return {'results': results}

@debug_bp.route('/channels')
def channels_debug():
    channelQuery = channels.channel.query.all()
    return {'results': [ob.serialize() for ob in channelQuery]}