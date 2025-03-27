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
                return checked_pswd
                
            else:
                print("Votre mail ou mot de passe est erroné, veuillez retenter.")
                Controller.start_session()

    class TokenController():    
        @staticmethod
        def generate_token(mail):
            payload = {
                "mail":mail,
                "exp":datetime.datetime.now() + datetime.timedelta(days=1)
            }
            secret_key = "clé_secrète"
            token = jwt.encode(payload, secret_key, algorithm='HS256')

        @staticmethod
        def decode_token(token, secret_key):
            try:
                decoded_payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                return decoded_payload
            except jwt.ExpiredSignatureError:
                print('Le token a expiré')
            except jwt.InvalidTokenError:
                print('Token non valide')
        
        @staticmethod
        def store_token(token):
            with open('.token', 'w') as f:
                f.write(f'{token}')
        
        @staticmethod
        def get_local_token():
            try:
                with open('.token', 'r') as f:
                    token = f.read()
                    return token
            except Exception as e:
                print(f"Token non trouvé en local : {e}")

        @staticmethod
        def get_permissions(payload):
            user = User.get(User.mail == payload["mail"])
            return user.role

