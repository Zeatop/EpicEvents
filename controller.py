import views
from models import *
import jwt

class Controller():

    class SessionController():     
        @staticmethod
        def create_account(user_infos:dict):
            User(user_infos["name"], user_infos["mail"], user_infos["phone"],
                 user_infos["password"], user_infos["role"])

        @staticmethod
        def start_session():
            data = views.Views.Connection()
            mail = data["mail"]
            password = data["password"]
            user = User.get(User.mail==mail)
            checked_pswd = Security.verify_password(password, user.password)
            if checked_pswd:
                Controller.TokenController.generate_token(mail)
                return checked_pswd
            else:
                print("Votre mail ou mot de passe est erroné, veuillez retenter.")
                Controller.start_session()
        
        @staticmethod
        def retrieve_session():
            token = Controller.TokenController.get_local_token()
            if token:
                token = Controller.TokenController.decode_token(token)
                exp = token["exp"]
                now = datetime.datetime.now()
                if exp < now:
                    print("token expiré, veuillez vous connecter à nouveau")
                else:
                    Controller.SessionController.start_session()
            else:
                Controller.SessionController.start_session()