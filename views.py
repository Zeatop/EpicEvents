from models import *


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
        role = input("Role: SUPPORT (1) - COMMERCIAL (2) - Management (3)")


        return {"name":name,
                "mail":mail,
                "phone":phone,
                "password":password,
                "role":int(role)}
    @staticmethod
    def remind_me():
        remind = input ("Souhaitez-vous enregistrer votre session pour la prochaine connexion ? \n  - Oui (tapez 1)\n  - Non (tapez 2)")
        return int(remind)

    @staticmethod
    def home_menu(user:User):
        match user.role:
            case "Management":
                home_choice = input("Que souhaitez-vous faire ? \n  - Créer un compte (tapez 1) \n  - Changer le statut d'un contrat (tapez 2) \n  - Quitter (tapez 3) \nChoix: ")
                choice = int(home_choice)
                return choice

            case "commercial":
                home_choice = input("Que souhaitez-vous faire ? \n  - Créer un client (tapez 1) \n  - Créer un contrat (tapez 2) \n  - Créer un évènement (tapez 2) \n  - Quitter (tapez 3) \nChoix: ")
                choice = int(home_choice)

            case "support":
                home_choice = input("Que souhaitez-vous faire ? \n  - Regarder les évènements (tapez 1) \nChoix: ")
                choice = int(home_choice)