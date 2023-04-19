from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_security import (
    current_user,
    login_required,
    roles_required,
    logout_user,
)

admin_bp = Blueprint('admin', __name__)

@login_required
@roles_required("Admin")
@admin_bp.route('/')
def admin_page():
    pass