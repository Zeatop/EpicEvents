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
                print("Mot de passe incorrect \nRéessayez de vous connecter")
                Controller.login()
                return None
        except User.DoesNotExist:
            print("Utilisateur non trouvé")
            exit(0)
        
    @staticmethod
    def handle_session_persistence(choice):
        if choice == 2:
            Token.delete_local_token()
        
    @staticmethod
    def create_account(user:User):
        account_infos = views.Views.create_user()
        match account_infos["role"]:
            case 1:
                account_infos["role"] = UserRole.SUPPORT.value
            case 2:
                account_infos["role"] = UserRole.COMMERCIAL.value
            case 3:
                account_infos["role"] = UserRole.MANAGEMENT.value

        if user.get_permission == Permissions.MANAGEMENT_TEAM:
            try:
                User.create_user(account_infos)
                print(f"Création du compte {account_infos['role'].value} réussie !")
            except Exception as e:
                print(f"Une erreur est survenue lors de la création du compte : {e}")
        else:
            print("Il faut être dans l'équipe de gestion pour créer un compte.")

    @staticmethod
    def action_selector(user:User, choice):
        match user.role:
            case "Management":
                if choice == 1:
                    Controller.create_account(user)
                elif choice == 2:
                    Event_Contract_Controller.create_contract(user)
                elif choice == 3:
                    Event_Contract_Controller.update_contract(user)
                elif choice == 4:
                    Event_Contract_Controller.update_event(user)
                elif choice == 5:
                    Controller.select_data_display(user)
                    pass
                elif choice == 6:
                    remind = views.Views.remind_me()
                    if int(remind) == 2:
                        Token.delete_local_token() 
                    exit(0)
                else:
                    print("Veuillez renseigner un choix valide")
                    views.Views.home_menu(user)
                    
            case "commercial":
                if choice == 1:
                    ClientController.create_client(user)
                elif choice == 2:
                    ClientController.update_client(user)
                elif choice == 3:
                    Event_Contract_Controller.update_contract(user)
                elif choice == 4:
                    Event_Contract_Controller.create_event(user)
                elif choice == 5:
                    Controller.select_data_display(user)
                elif choice == 6:
                    remind = views.Views.remind_me()
                    if int(remind) == 2:
                        Token.delete_local_token() 
                    exit(0)
                else:
                    print("Veuillez renseigner un choix valide")
                    views.Views.home_menu(user)

            case "support":
                if choice == 1:
                    Controller.select_data_display(user)
                    pass
                elif choice == 2:
                    remind = views.Views.remind_me()
                    if int(remind) == 2:
                        Token.delete_local_token() 
                    exit(0)
                else:
                    print("Veuillez renseigner un choix valide")
                    views.Views.home_menu(user)

    @staticmethod
    def select_data_display (user:User):
        choice = views.Views.select_data_display(user)
        match user.role:
            case "Management":
                match choice:
                    case 1:
                        views.Views.show_all_data()
                    case 2:
                        views.Views.show_unsupported_events()
                    case _:
                        print("Veuillez renseigner un choix valide")
                        views.Views.select_data_display(user)

            case "commercial":
                match choice:
                    case 1:
                        views.Views.show_all_data()
                    case 2:
                        views.Views.show_unsigned_contracts()
                    case 3:
                        views.Views.show_unsigned_contracts()
                    case _:
                        print("Veuillez renseigner un choix valide")
                        views.Views.select_data_display(user)           

            case "support":
                match choice:
                    case 1:
                        views.Views.show_all_data()
                    case 2:
                        views.Views.show_my_events(user)
                    case _:
                        print("Veuillez renseigner un choix valide")
                        views.Views.home_menu(user)
                                            


class ClientController():

    def create_client(user:User):
        if user.get_permission == Permissions.COMMERCIAL_TEAM:
            client_infos = views.Views.create_client()
            try:
                Client.create_client(client_infos)
                print(f"Création du client {client_infos['name'].value} réussie !")
            except Exception as e:
                print(f"Une erreur est survenue lors de la création du client : {e}\nVeuillez réessayer.")
                ClientController.create_client(user)
        else:
            print("Il faut être dans l'équipe commerciale pour créer un client.")
    
    def update_client(user:User):
        if user.get_permission == Permissions.COMMERCIAL_TEAM:
            choice = views.Views.select_client_update()
            client = views.Views.select_client()
            match choice:
                case 1:
                    new_phone = views.Views.update_client_phone()
                    client.update_phone(new_phone)
                case 2:
                    new_mail = views.Views.update_client_mail()
                    client.update_mail(new_mail)
                case _:
                    print("Veuillez renseigner un choix valide")
                    ClientController.update_client(user)

        else:
            print("Il faut être dans l'équipe commerciale pour mettre à jour un client.")


class Event_Contract_Controller():

    def create_contract(user:User):
        if user.get_permission == Permissions.MANAGEMENT_TEAM:
            contract_infos = views.Views.create_contract()
            try:
                Contract.create_contract(contract_infos)
                print(f"Création du {contract_infos['name'].value} réussie !")
            except Exception as e:
                print(f"Une erreur est survenue lors de la création du contrat : {e}\nVeuillez réessayer")
                Event_Contract_Controller.create_contract(user)
        else:
            print("Il faut être dans l'équipe gestion pour créer un contrat.")

    def update_contract(user:User):
        if user.get_permission == Permissions.COMMERCIAL_TEAM or user.get_permission == Permissions.MANAGEMENT_TEAM :
            contract = views.Views.select_contract()
            match user.get_permission:
                case Permissions.MANAGEMENT_TEAM:
                    new_state = views.Views.update_contract_state()
                    contract.update_contract_state(new_state)
                case Permissions.COMMERCIAL_TEAM:
                    #TODO Rajouter condition du client que le commercial a créé
                    amount = views.Views.update_rest_amount()
                    contract.update_rest_amount(amount)
        else:
            print("Il faut être dans l'équipe commerciale ou gestionnaire pour mettre à jour un client.")

    def create_event(user:User):
        if user.get_permission == Permissions.COMMERCIAL_TEAM:
            event_infos = views.Views.create_event()
            try:
                Event.create_event(event_infos)
                print(f"Création de l'évènement {event_infos['name'].value} réussie !")
            except Exception as e:
                print(f"Une erreur est survenue lors de la création de l'évènement : {e}\Veuillez réessayer.")
                Event_Contract_Controller.create_event(user)
        else:
            print("Il faut être dans l'équipe commerciale pour créer un évènement.")
    
    def update_event(user:User):
        if user.get_permission == Permissions.MANAGEMENT_TEAM:
            event = views.Views.select_event()
            logistic_contact = views.Views.add_support()
            event.add_support(logistic_contact)
        else:
            print("Il faut être dans l'équipe de commerciale pour mettre à jour un évènement.")
            
    

