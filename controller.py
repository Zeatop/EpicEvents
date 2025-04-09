import views
from models import *
import jwt

class DBController():
    def db_startup():
        db.connect()
        try:
            db.create_tables([User, Contract, Event, Client], safe=True)
            # Vérifier si l'utilisateur root existe
            try:
                User.get(User.name=="root")
            except User.DoesNotExist:
                # Créer l'utilisateur root s'il n'existe pas
                root_infos = {
                    "name":"root",
                    "mail": "root@root.com",
                    "phone": "rootphone",
                    "password": "root",
                    "role": UserRole.MANAGEMENT.value
                }
                User.create_user(root_infos)
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base de données: {e}")

class Controller():

    @staticmethod
    def create_account():
        user_infos = views.Views.create_user()
        try:
            print(f"Création de l'utilisateur {user_infos['mail']} en cours...")
            user = User.create_user(user_infos)
            print(f"Création de l'utilisateur {user_infos['mail']} réussie !")
            return user
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur: {e}")

    @staticmethod
    def login():
        token = Token.get_local_token()
        if token:
            payload = Token.decode_token(token, SECRET_KEY)
            is_token_valid = Token.is_valid(payload) 
            if is_token_valid:
                mail = payload['mail']
                user =  User.get(User.mail == mail)
                return user

        user_infos = views.Views.connection()
        try:
            user = User.get(User.mail == user_infos["mail"])
            if Security.verify_password(user_infos["password"], user.password):
                token = Token.generate_token(user.mail)
                Token.store_token(token)
                print(f"Connexion réussie pour {user.name}")
                return user
            else:
                print("Mot de passe incorrect")
                return None
        except User.DoesNotExist:
            print("Utilisateur non trouvé")
            return None
        
    @staticmethod
    def handle_session_persistence(choice):
        if choice == 2:
            Token.delete_local_token()
        
    @staticmethod
    def create_account(user:User):
        account_infos = views.Views.create_user()
        if user.get_permission() == Permissions.MANAGEMENT_TEAM:
            try:
                User.create_user(account_infos)
                print(f"Création du compte {account_infos['role']} réussie !")
            except Exception as e:
                print(f"Une erreur est survenue lors de la création du compte : {e}")
        else:
            print("Il faut être dans l'équipe de gestion pour créer un compte.")
    
    @staticmethod
    def action_selector(user, choice):
        match user.role:
            case "Management":
                if choice == 1:
                    account_infos = views.Views.create_user()
                    return account_infos
                if choice == 2:
                    pass
                if choice == 3:
                    remind = views.Views.remind_me()
                    if int(remind) == 2:
                        Token.delete_local_token() 
                    exit(0)
                else:
                    print("Veuillez renseigner un choix valide")
                    views.Views.home_menu(user)
            case "commercial":
                pass

            case "support":
                pass



