from controller import *

SentryController.init_sentry()
DBController.db_startup()
user = Controller.login()
while True:
    choice = views.Views.home_menu(user)
    Controller.action_selector(user, choice)