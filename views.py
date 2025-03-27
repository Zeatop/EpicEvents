from models import *


class Views():
    
    @staticmethod
    def Connection():
        wish = input("Connectez-vous: (1) \nCréer un compte: press(2)" )
        mail = input("Votre email: ")
        password = input("Votre mot de passe: ")
        return {"mail":mail,
                "password":password
                }
   
        # name = input("Votre nom: ")
        # mail = input("Votre mail:")
        # phone = input ("Votre numéro de téléphone: ")
        # password = input("Votre mot de passe:")
        # role = input("")
        # return {"name":name,
        #         "mail":mail,
        #         "phone":phone,
        #         "password":password,
        #         "role":role}