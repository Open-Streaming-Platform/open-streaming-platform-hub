import datetime
from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    current_user,
    login_required,
    roles_required,
    logout_user,
)
from flask_security.utils import hash_password
from functions import system
from classes import servers
from classes import channels
from classes import sec
from classes.shared import db

root_bp = Blueprint('root', __name__)

@root_bp.route('/')
def landing_page():
    firstRunCheck = system.check_existing_user()
    if firstRunCheck is False:
        return render_template('/firstrun.html')
    else:
        return render_template('/index.html')

@root_bp.route('/registerFirstRun', methods=["POST"])
def register_first_run():
    firstRunCheck = system.check_existing_user()
    if firstRunCheck is False:
            
            username = request.form["username"]
            emailAddress = request.form["email"]
            password1 = request.form["password1"]
            password2 = request.form["password2"]
            
            if password1 == password2:
                from app import user_datastore
                
                passwordhash = hash_password(password1)

                user_datastore.create_user(
                    email=emailAddress, username=username, password=passwordhash
                )
                db.session.commit()
                user = sec.User.query.filter_by(username=username).first()
                user.confirmed_at = datetime.datetime.utcnow()

                user_datastore.find_or_create_role(
                    name="Admin", description="Administrator"
                )

                user_datastore.add_role_to_user(user, "Admin")
                db.session.commit()
            else:
            
                flash("Passwords do not match")
                return redirect(url_for(".landing_page"))

    return redirect(url_for(".landing_page"))
    