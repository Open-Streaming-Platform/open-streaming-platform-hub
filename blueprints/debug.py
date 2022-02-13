from flask import Blueprint, request, url_for, render_template, redirect, flash
from classes import servers
from classes import channels

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/servers')
def servers_debug():
    serverQuery = servers.server.query.all()
    return {'results': [ob.serialize() for ob in serverQuery]}

@debug_bp.route('/channels')
def channels_debug():
    channelQuery = channels.channel.query.all()
    return {'results': [ob.serialize() for ob in channelQuery]}