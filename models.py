from enum import Enum, auto
import datetime
from peewee import *
import jwt
import bcrypt
import os

db = SqliteDatabase('EpicEvents.db')
SECRET_KEY = "clé_secrète"

class Permissions(Enum):

    MANAGEMENT_TEAM = auto()
    LOGISTIC_TEAM = auto()
    COMMERCIAL_TEAM = auto()

class UserRole (Enum):
    
    SUPPORT = "support"
    COMMERCIAL = "commercial"
    MANAGEMENT = "Management"

class Security():
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def verify_password(password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

class User(Model):
    name = CharField()
    mail = CharField(unique=True)
    phone = CharField()
    password = CharField()
    role = CharField(choices=((r.value, r.name) for r in UserRole))

    class Meta:
        database = db

    @property
    def get_permission(self):
        match self.role:
            case UserRole.SUPPORT.value:
                return Permissions.LOGISTIC_TEAM
            case UserRole.COMMERCIAL.value:
                return Permissions.COMMERCIAL_TEAM
            case UserRole.MANAGEMENT.value:
                return Permissions.MANAGEMENT_TEAM
        
    @classmethod
    def create_user(cls, account_infos:dict):
        hashed_password = Security.hash_password(account_infos["password"])
        user = cls.create(name=account_infos["name"], mail=account_infos["mail"],
                          phone=account_infos["phone"], password=hashed_password,
                          role=account_infos["role"])
        return user

class Client(Model):
    name = CharField()
    mail = CharField()
    phone = CharField()

    class Meta:
        database = db
    
    @classmethod
    def create_client(cls, client_infos:dict):
        user = cls.create(name=["name"], mail=["mail"], phone=["phone"])
        return user
    
    def update_phone(self, phone):
        self.phone = phone
        self.save()
    
    def update_mail(self, mail):
        self.phone = mail
        self.save()

class Token(Model):

    @classmethod
    def generate_token(cls, mail):
        expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        payload = {
            "mail":mail,
            "exp":expiration.timestamp()
        }
        encoded_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return encoded_token
    
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
    def decode_token(token, secret_key):
        try:
            decoded_payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return decoded_payload
        except jwt.ExpiredSignatureError:
            print('Le token a expiré')
            return None
        except jwt.InvalidTokenError:
            print('Token non valide')
            return None

    @classmethod
    def is_valid(cls, payload):
        # Vérifier si le token existe en base et n'est pas expiré
        try:
            expiration = payload['exp']
            current_timestamp = datetime.datetime.now().timestamp()
            return  current_timestamp < expiration
        except cls.DoesNotExist:
            return False

    @staticmethod
    def get_permissions(payload):
        user = User.get(User.mail == payload["mail"])
        return user.role
    
    @staticmethod
    def delete_local_token():
        try:
            os.remove('.token')
            print("Token local supprimé.")
        except FileNotFoundError:
            print("Aucun token local à supprimer.")
        except Exception as e:
            print(f"Erreur lors de la suppression du token local : {e}")

class Contract(Model):
    client = ForeignKeyField(Client, backref='contracts')
    commercial = ForeignKeyField(User, backref='contracts')
    total_amount = DecimalField()
    rest_amount = DecimalField()
    state = CharField()
    date_created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

    @classmethod
    def create_contract(cls, contract_dict:dict):
        contract = cls.create(client=contract_dict["client"], commercial=contract_dict["commercial"], total_amount=contract_dict["total_amount"],
                   rest_amount=contract_dict["rest_amount"], state=contract_dict["state"])
        return contract
    
    def update_contract_state(self, state):
        self.state = state
        self.save()
    
    def update_rest_amount(self, amount):
        self.rest_amount = self.rest_amount - amount
        self.save()   

class Event(Model):
    contract = ForeignKeyField(Contract, backref='events')
    client = ForeignKeyField(User, backref='events')
    name = CharField(unique=True)
    event_start = DateTimeField()
    event_end = DateTimeField()
    logistic_contact = ForeignKeyField(User, backref='events')
    location = CharField()
    attendees = IntegerField()
    notes = TextField(null=True)

    class Meta:
        database = db
    
    @classmethod
    def create_event(cls, contract_infos:dict):
        event = cls.create(contract=contract_infos["contract"], client=contract_infos["client"], event_start=contract_infos["event_start"], event_end=contract_infos["event_end"],
                   logistic_contact=contract_infos["logistic_contact"],location=contract_infos["location"], attendees=contract_infos["attendees"], notes=contract_infos["notes"])
        return event
    
    def add_support(self, logistic_contact:User):
        self.logistic_contact = logistic_contact