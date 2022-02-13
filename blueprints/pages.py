from flask import Blueprint, request, url_for, render_template, redirect, flash
from classes import servers
from classes import channels

root_bp = Blueprint('root', __name__)

@root_bp.route('/')
def landing_page():
    serverQuery = servers.server.query.all()
    channelQuery = channels.channel.query.filter_by(channelLive=True)
    return render_template('/index.html', serverList=serverQuery, channelList=channelQuery)
