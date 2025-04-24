import views
from models import *
import sentry_sdk
import jwt

DEBUG = True
class SentryController():

    """Gère l'intégration avec Sentry pour le suivi des erreurs."""

    @staticmethod
    def init_sentry():

        """Initialise la configuration Sentry pour le monitoring des erreurs."""

        sentry_sdk.init(
        dsn="https://2f9cb531ca3820e0aba34c3daf1db2a0@o4509147190460416.ingest.de.sentry.io/4509147194196048",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        )

class DBController():
    def db_startup():

        """Initialise la base de données et crée les tables et utilisateurs par défaut."""

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
            if DEBUG == True:
                try:
                    User.get(User.name=="TestCom")
                except User.DoesNotExist:
                    # Créer l'utilisateur root s'il n'existe pas
                    commercial_infos = {
                        "name":"TestCom",
                        "mail": "TestCom",
                        "phone": "TestCom",
                        "password": "test",
                        "role": UserRole.COMMERCIAL.value
                    }
                    User.create_user(commercial_infos)
                try:
                    User.get(User.name=="TestSup")
                except User.DoesNotExist:
                    # Créer l'utilisateur root s'il n'existe pas
                    support_infos = {
                        "name":"TestSup",
                        "mail": "TestSup",
                        "phone": "TestSup",
                        "password": "test",
                        "role": UserRole.SUPPORT.value
                    }
                    User.create_user(support_infos)
        except Exception as e:
            print(Colors.error(f"Erreur lors de l'initialisation de la base de données: {e}"))

class FlowController():

    """Contrôle le flux principal de l'application et la navigation entre fonctionnalités."""

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
                print(Colors.success(f"Connexion réussie pour {user.name}"))
                return user
            else:
                print(Colors.error("Mot de passe incorrect \nRéessayez de vous connecter"))
                return FlowController.login()
                
        except User.DoesNotExist:
            print(Colors.error("Utilisateur non trouvé"))
            return FlowController.login()
        
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

        if user.get_permission != Permissions.MANAGEMENT_TEAM:
            print(Colors.info("Il faut être dans l'équipe de gestion pour créer un compte."))
            return
        try:
            User.create_user(account_infos)
            print(Colors.success(f"Création du compte {account_infos['role']} réussie !"))
        except Exception as e:
            print(Colors.error(f"Une erreur est survenue lors de la création du compte : {e}"))
            

    @staticmethod
    def action_selector(user:User, choice):
        match user.role:
            case "Management":
                if choice == 1:
                    FlowController.create_account(user)
                elif choice == 2:
                    Event_Contract_Controller.create_contract(user)
                elif choice == 3:
                    Event_Contract_Controller.update_contract(user)
                elif choice == 4:
                    Event_Contract_Controller.update_event(user)
                elif choice == 5:
                    FlowController.select_data_display(user)
                    pass
                elif choice == 6:
                    remind = views.Views.remind_me()
                    if int(remind) == 2:
                        Token.delete_local_token() 
                    exit(0)
                else:
                    print(Colors.error("Veuillez renseigner un choix valide"))
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
                    FlowController.select_data_display(user)
                elif choice == 6:
                    remind = views.Views.remind_me()
                    if int(remind) == 2:
                        Token.delete_local_token() 
                    exit(0)
                else:
                    print(Colors.error("Veuillez renseigner un choix valide"))
                    views.Views.home_menu(user)

            case "support":
                if choice == 1:
                    FlowController.select_data_display(user)
                    pass
                elif choice == 2:
                    remind = views.Views.remind_me()
                    if int(remind) == 2:
                        Token.delete_local_token() 
                    exit(0)
                else:
                    print(Colors.error("Veuillez renseigner un choix valide"))
                    views.Views.home_menu(user)

    @staticmethod
    def select_data_display (user:User):
        choice = views.Views.select_data_display(user)
        match user.role:
            case "Management":
                match choice:
                    case 1:
                        contracts = Contract.select()
                        views.Views.show_all_data(contracts)
                    case 2:
                        events = Event.select().where(Event.logistic_contact.is_null())
                        views.Views.show_unsupported_events(events)
                    case _:
                        print(Colors.error("Veuillez renseigner un choix valide"))
                        views.Views.select_data_display(user)

            case "commercial":
                match choice:
                    case 1:
                        contracts = Contract.select()
                        views.Views.show_all_data(contracts)
                    case 2:
                        contracts = Contract.select().where(Contract.state != "Signé")
                        views.Views.show_unsigned_contracts(contracts)
                    case 3:
                        contracts = Contract.select().where(Contract.rest_amount != 0)
                        views.Views.show_unpaid_contracts(contracts)
                    case _:
                        print(Colors.error("Veuillez renseigner un choix valide"))
                        views.Views.select_data_display(user)           

            case "support":
                match choice:
                    case 1:
                        contracts = Contract.select()
                        views.Views.show_all_data(contracts)
                    case 2:
                        events = Event.select().where(Event.logistic_contact == user)
                        views.Views.show_my_events(events)
                    case _:
                        print(Colors.error("Veuillez renseigner un choix valide"))
                        views.Views.home_menu(user)

class ClientController():

    """Gère les opérations liées aux clients."""

    def create_client(user:User):
        if user.get_permission != Permissions.COMMERCIAL_TEAM:
            print(Colors.info("Il faut être dans l'équipe commerciale pour créer un client."))
            return
        client_infos = views.Views.create_client()
        try:
            Client.create_client(client_infos)
            print(Colors.success(f"Création du client {client_infos['name']} réussie !"))
        except Exception as e:
            print(Colors.error(f"Une erreur est survenue lors de la création du client : {e}\nVeuillez réessayer."))
            ClientController.create_client(user)        
    
    def update_client(user:User):
        if user.get_permission != Permissions.COMMERCIAL_TEAM:
            print(Colors.info("Il faut être dans l'équipe commerciale pour mettre à jour un client."))
            return
        clients = Client.select()
        client = views.Views.select_client(clients)
        if not client:
            return
        choice = views.Views.select_client_update()
        match choice:
            case 1:
                new_phone = views.Views.update_client_phone()
                client.update_phone(new_phone)
            case 2:
                new_mail = views.Views.update_client_mail()
                client.update_mail(new_mail)
            case _:
                print(Colors.error("Veuillez renseigner un choix valide"))
                ClientController.update_client(user)

class Event_Contract_Controller():

    """Gère les opérations liées aux contrats et événements."""

    def create_contract(user:User):
        
        clients = Client.select()
        client = views.Views.select_client(clients)
        if not client:
            return
        commercials = User.select().where(User.role == "commercial")
        commercial = views.Views.select_commercial(commercials)
        if not commercial:
            return
        contract_infos = views.Views.create_contract(user, client, commercial)
        if not contract_infos:
            return
        contract = Contract.create_contract(contract_infos)
        if contract:
            print(Colors.success(f"Création du {contract} réussie !"))      
            
    def update_contract(user:User):
        
        contracts = Contract.select()
        contract = views.Views.select_contract(user, contracts)
        if not contract:
            return
        match user.get_permission:
            case Permissions.MANAGEMENT_TEAM:
                new_state = views.Views.update_contract_state()
                contract.update_contract_state(new_state)
            case Permissions.COMMERCIAL_TEAM:
                #TODO Rajouter condition du client que le commercial a créé
                amount = views.Views.update_rest_amount()
                if amount == None  or amount == 0: 
                    return
                contract.update_rest_amount(amount)

    def create_event(user:User):
        
        contracts = Contract.select()
        event_infos = views.Views.create_event(user, contracts)
        if not event_infos:
            return
        event = Event.create_event(event_infos)
        if event:
            print(Colors.success(f"Création de l'évènement {event_infos['name']} réussie !")) 
    
    def update_event(user:User):

        events = Event.select()
        event = views.Views.select_event(user, events)
        if not event:
            return
        supports = User.select().where(User.role == "support")
        logistic_contact = views.Views.add_support(user, supports)
        logistic_contact = User.get(User.id == logistic_contact)
        added = event.add_support(logistic_contact)
        if added:
            print(Colors.success(f"Ajout de {logistic_contact.name} à l'évènement {event.name} réussie !"))
            
            
    

