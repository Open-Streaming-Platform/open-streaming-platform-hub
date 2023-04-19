from classes import sec
from classes.shared import db

def check_existing_user():
    userQuery = sec.User.query.all()
    if userQuery != []:
        db.session.close()
        return True
    else:
        db.session.close()
        return False