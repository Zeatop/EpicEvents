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
                                "\t- Voir les contrats (tapez 4)\n"
                                "\t- Créer un évènement (tapez 5)\n"
                                "\t- Créer un évènement (tapez 6)\n"
                                "\t- Voir la liste des contrats et évènements (tapez 7)\n"
                                "\t- Quitter (tapez 8)\n"
                                "\tChoix: ")
                choice = int(home_choice)
                return choice

            case "support":
                home_choice = input("Que souhaitez-vous faire ? \n"
                                    "\t- Regarder mes évènements (tapez 1) \n"
                                    "\t- Voir la liste des contrats et évènements (tapez 2)\n"
                                    "\tChoix: ")
                choice = int(home_choice)
                return choice