from models import *


class Views():
    
    @staticmethod
    def Connection():
        wish = input("Connectez-vous: (1) \nCréer un compte: press(2)" )
        match wish:
            case 1:
                pass
            case 2:
                name = input("Votre nom: ")
                mail = input("Votre mail:")
                phone = input ("Votre numéro de téléphone: ")
                password = input("Votre mot de passe:")
                role = input("")
                return {"name":name,
                        "mail":mail,
                        "phone":phone,
                        "password":password,
                        "role":role}