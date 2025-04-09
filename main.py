from controller import *

DBController.db_startup()
user = Controller.login()
choice = views.Views.home_menu(user)
Controller.action_selector(user, choice)