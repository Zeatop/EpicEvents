from enum import Enum, auto
import datetime
from peewee import *

db = SqliteDatabase('ma_base_de_donnees.db')

class Permissions(Enum):

    MANAGEMENT_TEAM = auto()
    LOGISTIC_TEAM = auto()
    COMMERCIAL_TEAM = auto()

class UserRole (Enum):
    
    CUSTOMER = "customer"
    SUPPORT = "support"
    COMMERCIAL = "commercial"
    MANAGEMENT_= "Management"

class User(Model):
    name = CharField()
    mail = CharField()
    phone = CharField()

    class Meta:
        database = db

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