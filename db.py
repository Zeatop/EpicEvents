from models import *

def db_startup():
    if User.get(User.name=="root"):
        db.connect()
    else:
        db.connect()
        db.create_tables([User, Contract, Event])
        User.create_user("root", "root@root.com", "rootphone", "root", UserRole.MANAGEMENT.value)