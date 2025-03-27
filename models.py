from enum import Enum, auto
import datetime
from peewee import *
import jwt
import bcrypt

db = SqliteDatabase('EpicEvents.db')
SECRET_KEY = "clé_secrète"

class Permissions(Enum):

    MANAGEMENT_TEAM = auto()
    LOGISTIC_TEAM = auto()
    COMMERCIAL_TEAM = auto()

class UserRole (Enum):
    
    CUSTOMER = "customer"
    SUPPORT = "support"
    COMMERCIAL = "commercial"
    MANAGEMENT = "Management"

class Security():
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

    def verify_password(password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

class User(Model):
    name = CharField()
    mail = CharField()
    phone = CharField()
    password = CharField()
    role = CharField(choices=((r.value, r.name) for r in UserRole))

    class Meta:
        database = db

    @property
    def get_permission(self):
        match self.role:
            case UserRole.CUSTOMER.value:
                return None
            case UserRole.SUPPORT.value:
                return Permissions.LOGISTIC_TEAM
            case UserRole.COMMERCIAL.value:
                return Permissions.COMMERCIAL_TEAM
            case UserRole.MANAGEMENT.value:
                return Permissions.MANAGEMENT_TEAM
        
    @classmethod
    def create_user(cls, name, mail, phone, password, role):
        hashed_password = Security.hash_password(password)
        user = cls.create(name=name, mail=mail, phone=phone, password=hashed_password, role=role)
        return user

class Token(Model):
    encoded_token = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    expires_at = DateTimeField()

    class Meta:
        database = db


    @classmethod
    def generate_token(cls, mail):
        expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        payload = {
            "mail":mail,
            "exp":expiration.timestamp()
        }
        encoded_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        token = cls.create(
            encoded_token = encoded_token,
            expires_at = expiration)
        
        return encoded_token

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
    def is_valid(cls, token_string):
        # Vérifier si le token existe en base et n'est pas expiré
        try:
            token = cls.get(cls.encoded_token == token_string)
            return datetime.datetime.now() < token.expires_at
        except cls.DoesNotExist:
            return False

    @staticmethod
    def get_permissions(payload):
        user = User.get(User.mail == payload["mail"])
        return user.role

class Session(Model):
    user =  ForeignKeyField(User, backref='sessions')
    token = ForeignKeyField(Token, backref='sessions')
    created_at = DateTimeField(default=datetime.datetime.now)
    expires_at = DateTimeField(default=(datetime.datetime.now() + datetime.timedelta(days=1)))

    class Meta:
        database = db

    @classmethod
    def create_session(cls, user):
        encoded_token = Token.generate_token(user.mail)
        token_object = Token.get(Token.encoded_token == encoded_token)
        expires_at = datetime.datetime.now() + datetime.timedelta(days=1)
        session = cls.create(
            user=user,
            token=token_object,
            expires_at=expires_at
        )
        return session
        
    def is_valid(self):
        return datetime.datetime.now() < self.expires_at
    
    @classmethod
    def get_active_session(cls, encoded_token):
        try: 
            token = cls.get(cls.encoded_token == encoded_token)
        except Token.DoesNotExist:
            return None
        decoded = Token.decode_token(token, SECRET_KEY)
        if not decoded:
            return None
        # Cherchez la session correspondante en BDD
        try:
            session = cls.get(cls.encoded_token == token)
            if session.is_valid():
                return session
            return None
        except cls.DoesNotExist:
            return None
        
    @classmethod
    def get_user_active_session(cls, user):
        current_time = datetime.datetime.now()
        try:
            # Jointure avec Token pour vérifier l'expiration
            return cls.select().join(Token).where(
                (cls.user == user) & 
                (Token.expires_at > current_time)
            ).order_by(cls.created_at.desc()).first()
        except:
            return None


class Contract(Model):
    client = ForeignKeyField(User, backref='contracts')
    commercial = ForeignKeyField(User, backref='contracts')
    total_amount = DecimalField()
    rest_amount = DecimalField()
    state = CharField()
    date_created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

class Event(Model):
    contract = ForeignKeyField(Contract, backref='events')
    client = ForeignKeyField(User, backref='events')
    event_start = DateTimeField()
    event_end = DateTimeField()
    logistic_contact = ForeignKeyField(User, backref='events')
    location = CharField()
    attendees = IntegerField()
    notes = TextField(null=True)

    class Meta:
        database = db