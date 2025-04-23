from models import *
from tabulate import tabulate
from colors import Colors

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
        print(Colors.highlight("Veuillez renseigner les informations du compte à créer"))
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
        print(Colors.highlight("Veuillez renseigner les informations du client à créer"))
        name = input("Nom: ")
        mail = input("Mail: ")
        phone = input("Numéro de téléphone: ")
        return {
            "name": name,
            "mail": mail,
            "phone": phone
        }

    @staticmethod
    def select_client(clients):
        print(Colors.highlight("\nListe des clients disponibles:"))
        
        if not clients:
            print(Colors.info("Aucun client n'est disponible."))
            return None
            
        for client in clients:
            print(Colors.prompt(f"ID: {client.id} - Nom: {client.name} - Mail: {client.mail} - Téléphone: {client.phone}"))
        
        client_id = input("\nSélectionnez l'ID du client à mettre à jour: ")
        
        try:
            selected_client = Client.get(Client.id == int(client_id))
            print(Colors.highlight(f"\nClient sélectionné: {selected_client.name}"))
            return selected_client
        except (Client.DoesNotExist, ValueError):
            print(Colors.error("Client invalide ou non trouvé."))
            return None
        
    @staticmethod
    def select_commercial(commercials):
        print(Colors.highlight("\nListe des commerciaux disponibles:"))
        
        if not commercials:
            print(Colors.info("Aucun Commercial n'est disponible."))
            return None
            
        for commercial in commercials:
            print(Colors.prompt(f"ID: {commercial.id} - Nom: {commercial.name}"))
        
        commercial_id = input("\nSélectionnez l'ID du Commercial à mettre à jour: ")
        
        try:
            selected_commercial = User.get(User.id == int(commercial_id))
            print(Colors.highlight(f"\nCommercial sélectionné: {selected_commercial.name}"))
            return selected_commercial
        except (User.DoesNotExist, ValueError):
            print(Colors.error("Commercial invalide ou non trouvé."))
            return None

    @staticmethod
    def select_client_update():
        print(Colors.highlight("\nQuelle mise à jour souhaitez-vous effectuer?"))
        print(Colors.prompt("1 - Mettre à jour le numéro de téléphone"))
        print(Colors.prompt("2 - Mettre à jour l'adresse mail"))
        
        choice = input("Votre choix (1 ou 2): ")
        return int(choice)

    @staticmethod
    def update_client_phone():
        new_phone = input("Nouveau numéro de téléphone: ")
        return new_phone

    @staticmethod
    def update_client_mail():
        new_mail = input("Nouvelle adresse mail: ")
        return new_mail

    @staticmethod
    def create_contract(user, client, commercial):

        if user.get_permission != Permissions.MANAGEMENT_TEAM:
            print(Colors.info("Il faut être dans l'équipe gestion pour créer un contrat."))
            return None

        print(Colors.highlight("Veuillez renseigner les informations du contrat à créer"))
        
        total_amount = input("Montant total: ")
        rest_amount = input("Montant restant à payer (par défaut même valeur que le montant total): ")
        
        # Si aucun montant restant n'est entré, utiliser le montant total
        if not rest_amount:
            rest_amount = total_amount
        
        print(Colors.highlight("\nÉtats possibles du contrat:"))
        print(Colors.prompt("1 - En attente"))
        print(Colors.prompt("2 - Signé"))
        state_choice = input("Sélectionnez l'état du contrat (1-2): ")
        
        states = {
            "1": "En attente",
            "2": "Signé",
        }
        
        state = states.get(state_choice, "En attente")
        
        return {
            "client": int(client.id),
            "commercial": int(commercial.id),
            "total_amount": float(total_amount),
            "rest_amount": float(rest_amount or total_amount),
            "state": state
        }
        
    @staticmethod
    def create_event(user, contracts):

        if user.get_permission != Permissions.COMMERCIAL_TEAM:
            print(Colors.info("Il faut être dans l'équipe commerciale pour créer un évènement."))
            return None
        print(Colors.highlight("Veuillez renseigner les informations de l'événement à créer"))
        
        # Afficher la liste des contrats existants
        print(Colors.highlight("\nListe des contrats disponibles:"))
        for contract in contracts:
            print(Colors.prompt(f"ID: {contract.id} - Client: {contract.client.name} - Commercial {contract.commercial.name}"))
        contract_id = input("Sélectionnez l'ID du contrat: ")
        
        # Le client est déjà associé au contrat, on le récupère automatiquement
        try:
            selected_contract = Contract.get(Contract.id == int(contract_id))
            client_id = selected_contract.client.id
            print(Colors.info(f"Client associé: {selected_contract.client.name}"))
        except Contract.DoesNotExist:
            print(Colors.error("Contrat non trouvé."))
            client_id = input("ID du client (saisie manuelle): ")
        
        name = input("Nom de l'événement: ")
        
        # Gestion des dates avec conversion en datetime
        import datetime
        
        print(Colors.highlight("\nDate et heure de début:"))
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
            print(Colors.error("Format de date invalide. Utilisation de la date et heure actuelles."))
            event_start = datetime.datetime.now()
        
        print(Colors.highlight("\nDate et heure de fin:"))
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
            print(Colors.error("Format de date invalide. Utilisation de la date actuelle + 1 jour."))
            event_end = datetime.datetime.now() + datetime.timedelta(days=1)

        location = input("Lieu de l'événement: ")
        attendees = input("Nombre de participants: ")
        notes = input("Notes supplémentaires (facultatif): ")
        # Liste des contacts de support disponibles
        print(Colors.highlight("\nListe des contacts logistiques disponibles:"))
        supports = User.select().where(User.role == "support")
        if not supports:
            return {
            "contract": int(contract_id),
            "client": int(client_id),
            "name": name,
            "event_start": event_start,
            "event_end": event_end,
            "location": location,
            "attendees": int(attendees) if attendees.isdigit() else 0,
            "notes": notes if notes else None
        }

        for support in supports:
            print(Colors.prompt(f"ID: {support.id} - Nom: {support.name}"))
        logistic_contact_id = input("Sélectionnez l'ID du contact logistique: ")
        
        return {
            "contract": int(contract_id),
            "client": int(client_id),
            "name": name,
            "event_start": event_start,
            "event_end": event_end,
            "logistic_contact": int(logistic_contact_id) if logistic_contact_id else None,
            "location": location,
            "attendees": int(attendees) if attendees.isdigit() else 0,
            "notes": notes if notes else None
        }

    @staticmethod
    def select_event(user, events):
        if user.get_permission != Permissions.MANAGEMENT_TEAM:
            print(Colors.info("Il faut être dans l'équipe gestion ajouter un support."))
            return None
        
        print(Colors.highlight("\nListe des événements disponibles:"))
        
        if not events:
            print(Colors.info("Aucun événement n'est disponible."))
            return None
            
        for event in events:
            print(Colors.prompt(f"ID: {event.id} - Nom: {event.name} - Date: {event.event_start} - Lieu: {event.location}"))
        
        event_id = input("\nSélectionnez l'ID de l'événement à mettre à jour: ")
        
        try:
            selected_event = Event.get(Event.id == int(event_id))
            print(Colors.highlight(f"\nÉvénement sélectionné: {selected_event.name} - Lieu: {selected_event.location}"))
            return selected_event
        except (Event.DoesNotExist, ValueError):
            print(Colors.error("Événement invalide ou non trouvé."))
            return None

    @staticmethod
    def select_contract(user, contracts):
        if user.get_permission == Permissions.LOGISTIC_TEAM:
            print(Colors.info("Il faut être dans l'équipe commerciale ou gestionnaire pour mettre à jour un contrat."))
            return
        print(Colors.highlight("\nListe des contrats disponibles:"))
         
        if not contracts:
            print(Colors.info("Aucun contrat n'est disponible."))
            return None
            
        for contract in contracts:
            print(Colors.prompt(f"ID: {contract.id} - Client: {contract.client.name} - État: {contract.state} - Montant restant: {contract.rest_amount}"))
        
        contract_id = input("\nSélectionnez l'ID du contrat à mettre à jour: ")
        
        try:
            selected_contract = Contract.get(Contract.id == int(contract_id))
            print(Colors.highlight(f"\nContrat sélectionné: {selected_contract.id} - Client: {selected_contract.client.name}"))
            return selected_contract
        except (Contract.DoesNotExist, ValueError):
            print(Colors.error("Contrat invalide ou non trouvé."))
            return None

    @staticmethod
    def update_rest_amount():
        print(Colors.highlight("\nMise à jour du montant restant à payer"))
        
        amount_input = input("Montant du paiement à déduire du reste à payer: ")
        
        try:
            amount = float(amount_input)
            if amount <= 0:
                print(Colors.error("Le montant doit être positif. Utilisez une valeur par défaut de 0."))
                return 0
            
            confirmation = input(f"Confirmer le paiement de {amount} € ? (O/N): ")
            if confirmation.upper() in ["O", "OUI", "Y", "YES"]:
                return amount
            else:
                print(Colors.info("Paiement annulé."))
                return 0
        except ValueError:
            print(Colors.error("Montant invalide. Veuillez entrer un nombre valide."))
            return 0

    @staticmethod
    def update_contract_state():
        print(Colors.highlight("\nÉtats possibles du contrat:"))
        print(Colors.prompt("1 - En attente"))
        print(Colors.prompt("2 - Signé"))
        state_choice = input("Sélectionnez le nouvel état du contrat (1-2): ")
        
        states = {
            "1": "En attente",
            "2": "Signé",
        }
        
        return states.get(state_choice, "En attente")

    @staticmethod
    def add_support(user, supports):

        if user.get_permission != Permissions.MANAGEMENT_TEAM:
            print(Colors.info("Il faut être dans l'équipe gestion pour ajouter un support."))
            return None
        # Liste des contacts de support disponibles
        print(Colors.highlight("\nListe des contacts logistiques disponibles:"))
        for support in supports:
            print(Colors.prompt(f"ID: {support.id} - Nom: {support.name}"))
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
    def show_all_data(contracts):
        
        # Préparation des données pour le tableau
        table_data = []
        for contract in contracts:
            events = list(contract.events)
            if events:
                for event in events:
                    table_data.append([
                        contract.state,
                        event.name, 
                        event.client.name, 
                        contract.commercial.name, 
                        event.logistic_contact.name if event.logistic_contact else "Non assigné"
                    ])
            else:
                table_data.append([
                contract.state,
                "Pas d'évènement prévu",
                contract.client.name,  # Utiliser directement le client du contrat
                contract.commercial.name,
                "Non assigné"
                ])
        
        # Définition des en-têtes
        headers = ["Contrat", "Évènement" , "Client", "Commercial", "Support"]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    @staticmethod
    def show_unsupported_events(events):
        
        # Préparation des données pour le tableau
        table_data = []
        for event in events:
            table_data.append([
                event.name, 
                event.contract.state, 
                event.client.name, 
                event.contract.commercial.name, 
                event.logistic_contact.name if event.logistic_contact else "Non assigné"
            ])
        
        # Définition des en-têtes
        headers = ["Évènement", "Contrat", "Client", "Commercial", "Support"]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    @staticmethod
    def show_my_events(events):
        
        # Préparation des données pour le tableau
        table_data = []
        for event in events:
            table_data.append([
                event.name, 
                event.contract.state, 
                event.client.name, 
                event.contract.commercial.name, 
                event.logistic_contact.name if event.logistic_contact else "Non assigné"
            ])
        
        # Définition des en-têtes
        headers = ["Évènement", "Contrat", "Client", "Commercial", "Support"]
        
        # Affichage du tableau
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    @staticmethod
    def show_unpaid_contracts(contracts):
        
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
    def show_unsigned_contracts(contracts):
        
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