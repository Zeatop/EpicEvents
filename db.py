from models import *

def db_startup():
    db.connect()
    db.create_tables([User, Contract, Event])
    User.create_user("root", "root@root.com", "rootphone", "root", UserRole.MANAGEMENT.value)