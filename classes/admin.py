from flask_security import current_user, url_for_security
from flask import request, redirect, url_for
from flask_admin import Admin, BaseView, expose, AdminIndexView

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        isAccessible = False
        if current_user.is_authenticated:
            if current_user.has_role('Admin'):
                isAccessible = True
        return isAccessible
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for_security('login', next=request.url))