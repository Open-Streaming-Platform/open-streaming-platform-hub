from flask import Blueprint, request, url_for, render_template, redirect, flash
from classes import servers
from classes import channels

root_bp = Blueprint('root', __name__)

@root_bp.route('/')
def landing_page():
    return render_template('/index.html')
