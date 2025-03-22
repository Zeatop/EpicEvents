from enum import Enum, auto
import datetime
from peewee import *
import jwt
import bcrypt

db = SqliteDatabase('EpicEvents .db')

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