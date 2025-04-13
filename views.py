from models import *
from tabulate import tabulate

class Views():
    
    @staticmethod
    def connection():
        mail = input("Votre email: ")
        password = input("Votre mot de passe: ")
        return {"mail":mail,
                "password":password
                }

    @staticmethod
    def create_user():
        print("Veuillez renseigner les informations du compte à créer")
        name = input("Nom: ")
        mail = input("Mail:")
        phone = input ("Numéro de téléphone: ")
        password = input("Mot de passe:")
        role = input("Role: SUPPORT (1) - COMMERCIAL (2) - Management (3) \nChoix: ")
        return {"name":name,
                "mail":mail,
                "phone":phone,
                "password":password,
                "role":int(role)
                }
    
    @staticmethod
    def remind_me():
        remind = input ("Souhaitez-vous enregistrer votre session pour la prochaine connexion ? \n  - Oui (tapez 1)\n  - Non (tapez 2) \nChoix:")
        return int(remind)

    @staticmethod
    def home_menu(user:User):
        match user.role:
            case "Management":
                home_choice = input("Que souhaitez-vous faire ?\n"
                               "\t- Créer un compte (tapez 1)\n"
                               "\t- Créer un contrat (tapez 2)\n"
                               "\t- Changer le statut d'un contrat (tapez 3)\n"
                               "\t- Ajouter un support à un évènement (tapez 4)\n"
                               "\t- Voir la liste des contrats et évènements (tapez 5)\n"
                               "\t- Quitter (tapez 6)\n"
                               "Choix: ")
                choice = int(home_choice)
                return choice

            case "commercial":
                home_choice = input("Que souhaitez-vous faire ?\n"
                                "\t- Créer un client (tapez 1)\n"
                                "\t- Mettre à jour un client (tapez 2)\n"
                                "\t- Mettre à jour un contrat (tapez 3)\n"
                                "\t- Créer un évènement (tapez 4)\n"
                                "\t- Voir la liste des contrats et évènements (tapez 5)\n"
                                "\t- Quitter (tapez 6)\n"
                                "\tChoix: ")
                choice = int(home_choice)
                return choice

            case "support":
                home_choice = input("Que souhaitez-vous faire ? \n"
                                    "\t- Voir la liste des contrats et évènements (tapez 1)\n"
                                    "\t- Quitter (tapez 2)\n"
                                    "\tChoix: ")
                choice = int(home_choice)
                return choice

    @staticmethod
    def create_client():
        print("Veuillez renseigner les informations du client à créer")
        name = input("Nom: ")
        mail = input("Mail: ")
        phone = input("Numéro de téléphone: ")
        return {
            "name": name,
            "mail": mail,
            "phone": phone
        }

    @staticmethod
    def select_client():
        print("\nListe des clients disponibles:")
        clients = Client.select()
        
        if not clients:
            print("Aucun client n'est disponible.")
            return None
            
        for client in clients:
            print(f"ID: {client.id} - Nom: {client.name} - Mail: {client.mail} - Téléphone: {client.phone}")
        
        client_id = input("\nSélectionnez l'ID du client à mettre à jour: ")
        
        try:
            selected_client = Client.get(Client.id == int(client_id))
            print(f"\nClient sélectionné: {selected_client.name}")
            return selected_client
        except (Client.DoesNotExist, ValueError):
            print("Client invalide ou non trouvé.")
            return None

    @staticmethod
    def select_client_update():
        print("\nQuelle mise à jour souhaitez-vous effectuer?")
        print("1 - Mettre à jour le numéro de téléphone")
        print("2 - Mettre à jour l'adresse mail")
        
        choice = input("Votre choix (1 ou 2): ")
        
        if choice in ["1", "2"]:
            return int(choice)
        else:
            print("Choix invalide. Sélection par défaut: mise à jour du numéro de téléphone.")
            return 1

    @staticmethod
    def update_client_phone():
        new_phone = input("Nouveau numéro de téléphone: ")
        return new_phone

    @staticmethod
    def update_client_mail():
        new_mail = input("Nouvelle adresse mail: ")
        return new_mail

    @staticmethod
    def create_contract():
        print("Veuillez renseigner les informations du contrat à créer")
        
        # Afficher la liste des clients existants
        print("\nListe des clients disponibles:")
        clients = Client.select()
        for client in clients:
            print(f"ID: {client.id} - Nom: {client.name}")
        client_id = input("Sélectionnez l'ID du client: ")
        
        # Afficher la liste des commerciaux
        print("\nListe des commerciaux disponibles:")
        commercials = User.select().where(User.role == "commercial")
        for commercial in commercials:
            print(f"ID: {commercial.id} - Nom: {commercial.name}")
        commercial_id = input("Sélectionnez l'ID du commercial: ")
        
        total_amount = input("Montant total: ")
        rest_amount = input("Montant restant à payer (par défaut même valeur que le montant total): ")
        
        # Si aucun montant restant n'est entré, utiliser le montant total
        if not rest_amount:
            rest_amount = total_amount
        
        print("\nÉtats possibles du contrat:")
        print("1 - En attente")
        print("2 - Signé")
        state_choice = input("Sélectionnez l'état du contrat (1-2): ")
        
        states = {
            "1": "En attente",
            "2": "Signé",
        }
        
        state = states.get(state_choice, "En attente")
        
        return {
            "client": int(client_id),
            "commercial": int(commercial_id),
            "total_amount": float(total_amount),
            "rest_amount": float(rest_amount or total_amount),
            "state": state
        }

    @staticmethod
    def create_event():
        print("Veuillez renseigner les informations de l'événement à créer")
        
        # Afficher la liste des contrats existants
        print("\nListe des contrats disponibles:")
        contracts = Contract.select()
        for contract in contracts:
            print(f"ID: {contract.id} - Client: {contract.client.name} - Commercial {contract.commercial.name}")
        contract_id = input("Sélectionnez l'ID du contrat: ")
        
        # Le client est déjà associé au contrat, on le récupère automatiquement
        try:
            selected_contract = Contract.get(Contract.id == int(contract_id))
            client_id = selected_contract.client.id
            print(f"Client associé: {selected_contract.client.name}")
        except Contract.DoesNotExist:
            print("Contrat non trouvé.")
            client_id = input("ID du client (saisie manuelle): ")
        
        name = input("Nom de l'événement: ")
        
        # Gestion des dates avec conversion en datetime
        import datetime
        
        print("\nDate et heure de début:")
        start_day = input("Jour (JJ): ")
        start_month = input("Mois (MM): ")
        start_year = input("Année (AAAA): ")
        start_hour = input("Heure (HH): ")
        start_minute = input("Minute (MM): ")
        
        try:
            event_start = datetime.datetime(
                int(start_year), int(start_month), int(start_day),
                int(start_hour), int(start_minute)
            )
        except ValueError:
            print("Format de date invalide. Utilisation de la date et heure actuelles.")
            event_start = datetime.datetime.now()
        
        print("\nDate et heure de fin:")
        end_day = input("Jour (JJ): ")
        end_month = input("Mois (MM): ")
        end_year = input("Année (AAAA): ")
        end_hour = input("Heure (HH): ")
        end_minute = input("Minute (MM): ")
        
        try:
            event_end = datetime.datetime(
                int(end_year), int(end_month), int(end_day),
                int(end_hour), int(end_minute)
            )
        except ValueError:
            print("Format de date invalide. Utilisation de la date actuelle + 1 jour.")
            event_end = datetime.datetime.now() + datetime.timedelta(days=1)
        
        # Liste des contacts de support disponibles
        print("\nListe des contacts logistiques disponibles:")
        supports = User.select().where(User.role == "support")
        for support in supports:
            print(f"ID: {support.id} - Nom: {support.name}")
        logistic_contact_id = input("Sélectionnez l'ID du contact logistique: ")
        
        location = input("Lieu de l'événement: ")
        attendees = input("Nombre de participants: ")
        notes = input("Notes supplémentaires (facultatif): ")
        
        return {
            "contract": int(contract_id),
            "client": int(client_id),
            "name": name,
            "event_start": event_start,
            "event_end": event_end,
            "logistic_contact": int(logistic_contact_id),
            "location": location,
            "attendees": int(attendees) if attendees.isdigit() else 0,
            "notes": notes if notes else None
        }

    @staticmethod
    def select_event():
        print("\nListe des événements disponibles:")
        events = Event.select()
        
        if not events:
            print("Aucun événement n'est disponible.")
            return None
            
        for event in events:
            print(f"ID: {event.id} - Nom: {event.name} - Date: {event.event_start} - Lieu: {event.location}")
        
        event_id = input("\nSélectionnez l'ID de l'événement à mettre à jour: ")
        
        try:
            selected_event = Event.get(Event.id == int(event_id))
            print(f"\nÉvénement sélectionné: {selected_event.name} - Lieu: {selected_event.location}")
            return selected_event
        except (Event.DoesNotExist, ValueError):
            print("Événement invalide ou non trouvé.")
            return None

    @staticmethod
    def select_contract():
        print("\nListe des contrats disponibles:")
        contracts = Contract.select()
        
        if not contracts:
            print("Aucun contrat n'est disponible.")
            return None
            
        for contract in contracts:
            print(f"ID: {contract.id} - Client: {contract.client.name} - État: {contract.state} - Montant restant: {contract.rest_amount}")
        
        contract_id = input("\nSélectionnez l'ID du contrat à mettre à jour: ")
        
        try:
            selected_contract = Contract.get(Contract.id == int(contract_id))
            print(f"\nContrat sélectionné: {selected_contract.id} - Client: {selected_contract.client.name}")
            return selected_contract
        except (Contract.DoesNotExist, ValueError):
            print("Contrat invalide ou non trouvé.")
            return None

    @staticmethod
    def update_rest_amount():
        print("\nMise à jour du montant restant à payer")
        
        amount_input = input("Montant du paiement à déduire du reste à payer: ")
        
        try:
            amount = float(amount_input)
            if amount <= 0:
                print("Le montant doit être positif. Utilisez une valeur par défaut de 0.")
                return 0
            
            confirmation = input(f"Confirmer le paiement de {amount} € ? (O/N): ")
            if confirmation.upper() in ["O", "OUI", "Y", "YES"]:
                return amount
            else:
                print("Paiement annulé.")
                return 0
        except ValueError:
            print("Montant invalide. Veuillez entrer un nombre valide.")
            return 0

    @staticmethod
    def update_contract_state():
        print("\nÉtats possibles du contrat:")
        print("1 - En attente")
        print("2 - Signé")
        print("3 - En cours")
        print("4 - Terminé")
        state_choice = input("Sélectionnez le nouvel état du contrat (1-4): ")
        
        states = {
            "1": "En attente",
            "2": "Signé",
            "3": "En cours",
            "4": "Terminé"
        }
        
        return states.get(state_choice, "En attente")

    @staticmethod
    def add_support():
        # Liste des contacts de support disponibles
        print("\nListe des contacts logistiques disponibles:")
        supports = User.select().where(User.role == "support")
        for support in supports:
            print(f"ID: {support.id} - Nom: {support.name}")
        logistic_contact_id = input("Sélectionnez l'ID du nouveau contact logistique: ")
        
        return int(logistic_contact_id)

    @staticmethod
    def select_data_display(user:User):
        match user.role:
            case "Management":
                data_choice = input("Que souhaitez-vous voir ?\n"
                               "\t- Tous les contrats et évènements (tapez 1)\n"
                               "\t- Les évènements sans support (tapez 2)\n"
                               "Choix: ")
                choice = int(data_choice)
                return choice

            case "commercial":
                data_choice = input("Que souhaitez-vous faire ?\n"
                                "\t- Tous les contrats et évènements (tapez 1)\n"
                                "\t- Les contrats non signés (tapez 2)\n"
                                "\t- Les contrats non régularisés (tapez 3)\n"
                                "\tChoix: ")
                choice = int(data_choice)
                return choice

            case "support":
                data_choice = input("Que souhaitez-vous voir ? \n"
                                    "\t- Tous les contrats et évènements (tapez 1) \n"
                                    "\t- Mes évènements attribués (tapez 2)\n"
                                    "\tChoix: ")
                choice = int(data_choice)
                return choice
 
    @staticmethod
    def show_all_data():
        events = Event.select()
        
        # Préparation des données pour le tableau
        table_data = []
        for event in events:
            table_data.append([
                event.name, 
                event.contract.state, 
                event.client.name, 
                event.commercial.name, 
                event.logistic_contact.name
            ])
        
        # Définition des en-têtes
        headers = ["Évènement", "Contrat", "Client", "Commercial", "Support"]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    @staticmethod
    def show_unsupported_events():
        events = Event.get(Event.logistic_contact == "None")
        
        # Préparation des données pour le tableau
        table_data = []
        for event in events:
            table_data.append([
                event.name, 
                event.contract.state, 
                event.client.name, 
                event.commercial.name, 
                event.logistic_contact.name
            ])
        
        # Définition des en-têtes
        headers = ["Évènement", "Contrat", "Client", "Commercial", "Support"]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    @staticmethod
    def show_my_events(user):
        events = Event.get(Event.logistic_contact == user)
        
        # Préparation des données pour le tableau
        table_data = []
        for event in events:
            table_data.append([
                event.name, 
                event.contract.state, 
                event.client.name, 
                event.commercial.name, 
                event.logistic_contact.name
            ])
        
        # Définition des en-têtes
        headers = ["Évènement", "Contrat", "Client", "Commercial", "Support"]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    @staticmethod
    def show_unpaid_contracts():
        contracts = Contract.get(Contract.rest_amount != 0)
        
        # Préparation des données pour le tableau
        table_data = []
        for contract in contracts:
            table_data.append([
                contract.state, 
                contract.rest_amount, 
                contract.state, 
                contract.client.name, 
                contract.commercial.name
            ])
        
        # Définition des en-têtes
        headers = ["Contrat", "Reste à payer", "État", "Client", "Commercial"]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    @staticmethod
    def show_unsigned_contracts():
        contracts = Contract.get(Contract.state != "Signé")
        
        # Préparation des données pour le tableau
        table_data = []
        for contract in contracts:
            table_data.append([
                contract.state, 
                contract.rest_amount, 
                contract.state, 
                contract.client.name, 
                contract.commercial.name
            ])
        
        # Définition des en-têtes
        headers = ["Contrat", "Reste à payer", "État", "Client", "Commercial"]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt="grid"))