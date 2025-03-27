import views
from models import *

class Controller():

    @staticmethod
    def create_account():
        pass

    @staticmethod
    def start_session():
        data = views.Views.Connection()
        mail = data["mail"]
        password = data["password"]
        user = User.get(User.mail==mail)
        checked_pswd = Security.verify_password(password, user.password)
        if checked_pswd:
            return checked_pswd
            
        else:
            print("Votre mail ou mot de passe est erroné, veuillez retenter.")
            Controller.start_session()
            