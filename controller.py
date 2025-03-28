import views
from models import *
import jwt

class DBController():
    def db_startup():
        if User.get(User.name=="root"):
            db.connect()
        else:
            db.connect()
            db.create_tables([User, Contract, Event])
            User.create_user("root", "root@root.com", "rootphone", "root", UserRole.MANAGEMENT.value)

class SessionController():

    @staticmethod
    def create_account():
        user_infos = views.Views.create_user()
        user = User.create_user(user_infos)
        return user

    @staticmethod
    def login():
        user_infos = views.Views.connection()
        user = User.get(User.mail == user_infos["mail"])
        is_session_active = Session.get_user_active_session(user)
        if is_session_active:
            pass
        else:
            session = Session.create_session(user)
        return session
    


