import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import datetime
from decimal import Decimal

# Importer les modules à tester
from models import User, Client, Contract, Event, Token, Security, UserRole, Permissions
from controller import Controller, ClientController, Event_Contract_Controller, DBController
from views import Views

class TestModels(unittest.TestCase):
    """Tests unitaires pour les modèles"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Utiliser une base de données en mémoire pour les tests
        from peewee import SqliteDatabase
        self.test_db = SqliteDatabase(':memory:')
        
        # Remplacer la base de données réelle par celle en mémoire
        models = [User, Client, Contract, Event]
        for model in models:
            model._meta.database = self.test_db
        
        # Créer les tables
        self.test_db.create_tables(models)
        
        # Données de test
        self.test_user_data = {
            "name": "TestUser",
            "mail": "test@example.com",
            "phone": "123456789",
            "password": "password123",
            "role": UserRole.MANAGEMENT.value
        }
        
        self.test_client_data = {
            "name": "TestClient",
            "mail": "client@example.com",
            "phone": "987654321"
        }
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.test_db.drop_tables([User, Client, Contract, Event])
        self.test_db.close()
    
    def test_user_creation(self):
        """Test la création d'un utilisateur"""
        user = User.create_user(self.test_user_data)
        self.assertEqual(user.name, "TestUser")
        self.assertEqual(user.mail, "test@example.com")
        self.assertEqual(user.role, UserRole.MANAGEMENT.value)
        
        # Vérifier que le mot de passe est bien hashé
        self.assertNotEqual(user.password, "password123")
        self.assertTrue(Security.verify_password("password123", user.password))
    
    def test_user_permissions(self):
        """Test les permissions d'un utilisateur"""
        # Test pour chaque rôle
        mgmt_user = User.create(name="Manager", mail="mgmt@test.com", phone="111", 
                               password="pass", role=UserRole.MANAGEMENT.value)
        com_user = User.create(name="Commercial", mail="com@test.com", phone="222", 
                             password="pass", role=UserRole.COMMERCIAL.value)
        support_user = User.create(name="Support", mail="support@test.com", phone="333", 
                                 password="pass", role=UserRole.SUPPORT.value)
        
        self.assertEqual(mgmt_user.get_permission, Permissions.MANAGEMENT_TEAM)
        self.assertEqual(com_user.get_permission, Permissions.COMMERCIAL_TEAM)
        self.assertEqual(support_user.get_permission, Permissions.LOGISTIC_TEAM)
    
    def test_client_creation(self):
        """Test la création d'un client"""
        client = Client.create_client(self.test_client_data)
        self.assertEqual(client.name, "TestClient")
        self.assertEqual(client.mail, "client@example.com")
        self.assertEqual(client.phone, "987654321")
    
    def test_client_update(self):
        """Test la mise à jour des informations d'un client"""
        client = Client.create_client(self.test_client_data)
        
        # Test mise à jour téléphone
        client.update_phone("111222333")
        self.assertEqual(client.phone, "111222333")
        
        # Test mise à jour email
        client.update_mail("new@example.com")
        self.assertEqual(client.mail, "new@example.com")
    
    def test_token_generation_and_validation(self):
        """Test la génération et validation de token"""
        # Créer un utilisateur
        user = User.create_user(self.test_user_data)
        
        # Générer un token
        token = Token.generate_token(user.mail)
        self.assertIsNotNone(token)
        
        # Décoder le token
        payload = Token.decode_token(token, "clé_secrète")
        self.assertIsNotNone(payload)
        self.assertEqual(payload['mail'], user.mail)
        
        # Vérifier validité
        self.assertTrue(Token.is_valid(payload))
        
    def test_contract_creation_and_update(self):
        """Test la création et mise à jour d'un contrat"""
        # Créer utilisateur et client pour le contrat
        user = User.create_user(self.test_user_data)
        client = Client.create_client(self.test_client_data)
        
        # Données du contrat
        contract_data = {
            "client": client.id,
            "commercial": user.id,
            "total_amount": 1000.0,
            "rest_amount": 1000.0,
            "state": "En attente"
        }
        
        # Créer le contrat
        contract = Contract.create_contract(contract_data)
        self.assertIsNotNone(contract)
        self.assertEqual(contract.state, "En attente")
        self.assertEqual(float(contract.total_amount), 1000.0)
        
        # Mettre à jour l'état
        contract.update_contract_state("Signé")
        self.assertEqual(contract.state, "Signé")
        
        # Mettre à jour le montant restant
        contract.update_rest_amount(500)
        self.assertEqual(float(contract.rest_amount), 500.0)
    
    def test_event_creation_and_support(self):
        """Test la création d'un événement et l'ajout de support"""
        # Créer utilisateur, client et contrat pour l'événement
        user = User.create_user(self.test_user_data)
        support_user = User.create(name="Support", mail="support@test.com", phone="333", 
                                 password="pass", role=UserRole.SUPPORT.value)
        client = Client.create_client(self.test_client_data)
        
        contract_data = {
            "client": client.id,
            "commercial": user.id,
            "total_amount": 1000.0,
            "rest_amount": 1000.0,
            "state": "Signé"
        }
        contract = Contract.create_contract(contract_data)
        
        # Données de l'événement
        event_data = {
            "contract": contract.id,
            "client": client.id,
            "name": "Test Event",
            "event_start": datetime.datetime.now(),
            "event_end": datetime.datetime.now() + datetime.timedelta(days=1),
            "location": "Test Location",
            "attendees": 100,
            "notes": "Test notes"
        }
        
        # Créer l'événement
        event = Event.create_event(event_data)
        self.assertIsNotNone(event)
        self.assertEqual(event.name, "Test Event")
        
        # Ajouter un support
        result = event.add_support(support_user)
        self.assertTrue(result)
        self.assertEqual(event.logistic_contact.id, support_user.id)


class TestFunctional(unittest.TestCase):
    """Tests fonctionnels pour l'application"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Utiliser une base de données en mémoire pour les tests
        from peewee import SqliteDatabase
        self.test_db = SqliteDatabase(':memory:')
        
        # Remplacer la base de données réelle par celle en mémoire
        models = [User, Client, Contract, Event]
        for model in models:
            model._meta.database = self.test_db
        
        # Créer les tables
        self.test_db.create_tables(models)
        
        # Créer les utilisateurs de test
        self.management_user = User.create(
            name="TestManager",
            mail="manager@test.com",
            phone="123",
            password=Security.hash_password("pass123"),
            role=UserRole.MANAGEMENT.value
        )
        
        self.commercial_user = User.create(
            name="TestCommercial",
            mail="commercial@test.com",
            phone="456",
            password=Security.hash_password("pass123"),
            role=UserRole.COMMERCIAL.value
        )
        
        self.support_user = User.create(
            name="TestSupport",
            mail="support@test.com",
            phone="789",
            password=Security.hash_password("pass123"),
            role=UserRole.SUPPORT.value
        )
        
        # Créer un client
        self.client = Client.create(
            name="TestClient",
            mail="client@test.com",
            phone="111222333"
        )
        
        # Créer un contrat
        self.contract = Contract.create(
            client=self.client,
            commercial=self.commercial_user,
            total_amount=2000,
            rest_amount=1500,
            state="En attente"
        )
        
        # Créer un événement
        self.event = Event.create(
            contract=self.contract,
            client=self.client,
            name="Annual Conference",
            event_start=datetime.datetime.now(),
            event_end=datetime.datetime.now() + datetime.timedelta(days=2),
            location="Conference Center",
            attendees=200,
            notes="Important event"
        )
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.test_db.drop_tables([User, Client, Contract, Event])
        self.test_db.close()
        
        # Supprimer fichier token s'il existe
        if os.path.exists('.token'):
            os.remove('.token')
    
    @patch('views.Views.connection')
    def test_login_success(self, mock_connection):
        """Test la connexion réussie"""
        # Simuler la saisie utilisateur
        mock_connection.return_value = {
            "mail": "manager@test.com",
            "password": "pass123"
        }
        
        # Test de la connexion
        user = Controller.login()
        self.assertIsNotNone(user)
        self.assertEqual(user.mail, "manager@test.com")
    
    
    @patch('views.Views.create_client')
    def test_create_client(self, mock_create_client):
        """Test la création d'un client"""
        # Simuler la saisie utilisateur
        mock_create_client.return_value = {
            "name": "New Client",
            "mail": "new@example.com",
            "phone": "999888777"
        }
        
        # Avant le test
        client_count = Client.select().count()
        
        # Créer un client
        ClientController.create_client(self.commercial_user)
        
        # Vérifier que le client a été créé
        self.assertEqual(Client.select().count(), client_count + 1)
        new_client = Client.get(Client.mail == "new@example.com")
        self.assertEqual(new_client.name, "New Client")
    
    @patch('views.Views.select_client')
    @patch('views.Views.select_commercial')
    @patch('views.Views.create_contract')
    def test_create_contract(self, mock_create_contract, mock_select_commercial, mock_select_client):
        """Test la création d'un contrat"""
        # Simuler les sélections utilisateur
        mock_select_client.return_value = self.client
        mock_select_commercial.return_value = self.commercial_user
        mock_create_contract.return_value = {
            "client": self.client.id,
            "commercial": self.commercial_user.id,
            "total_amount": 3000.0,
            "rest_amount": 3000.0,
            "state": "En attente"
        }
        
        # Avant le test
        contract_count = Contract.select().count()
        
        # Créer un contrat
        Event_Contract_Controller.create_contract(self.management_user)
        
        # Vérifier que le contrat a été créé
        self.assertEqual(Contract.select().count(), contract_count + 1)
        new_contract = Contract.get(Contract.id != self.contract.id)
        self.assertEqual(float(new_contract.total_amount), 3000.0)
    
    @patch('views.Views.select_contract')
    @patch('views.Views.update_contract_state')
    def test_update_contract_state(self, mock_update_contract_state, mock_select_contract):
        """Test la mise à jour de l'état d'un contrat"""
        # Simuler les sélections utilisateur
        mock_select_contract.return_value = self.contract
        mock_update_contract_state.return_value = "Signé"
        
        # État initial
        self.assertEqual(self.contract.state, "En attente")
        
        # Mettre à jour l'état du contrat
        Event_Contract_Controller.update_contract(self.management_user)
        
        # Vérifier la mise à jour
        updated_contract = Contract.get(Contract.id == self.contract.id)
        self.assertEqual(updated_contract.state, "Signé")
    
    @patch('views.Views.select_event')
    @patch('views.Views.add_support')
    def test_update_event_support(self, mock_add_support, mock_select_event):
        """Test l'ajout d'un support à un événement"""
        # Simuler les sélections utilisateur
        mock_select_event.return_value = self.event
        mock_add_support.return_value = self.support_user.id
        
        # État initial
        self.assertIsNone(self.event.logistic_contact)
        
        # Ajouter un support
        Event_Contract_Controller.update_event(self.management_user)
        
        # Vérifier la mise à jour
        updated_event = Event.get(Event.id == self.event.id)
        self.assertIsNotNone(updated_event.logistic_contact)
        self.assertEqual(updated_event.logistic_contact.id, self.support_user.id)

    @patch('os.remove')
    def test_handle_session_persistence(self, mock_remove):
        """Test la suppression du token lors de la déconnexion"""
        Controller.handle_session_persistence(2)
        mock_remove.assert_called_once()
        
        # Réinitialiser le mock
        mock_remove.reset_mock()
        
        # Tester qu'aucune suppression n'est effectuée quand l'utilisateur veut rester connecté
        Controller.handle_session_persistence(1)
        mock_remove.assert_not_called()

    @patch('controller.db.create_tables')
    @patch('controller.db.connect')
    def test_db_startup(self, mock_connect, mock_create_tables):
        """Test l'initialisation de la base de données"""
        with patch.object(User, 'get', side_effect=User.DoesNotExist):
            with patch.object(User, 'create_user') as mock_create_user:
                DBController.db_startup()
                
                # Vérifier que la connexion est établie
                mock_connect.assert_called_once()
                
                # Vérifier que les tables sont créées
                mock_create_tables.assert_called_once()
                
                # Vérifier que l'utilisateur root est créé
                mock_create_user.assert_called()

    @patch('views.Views.create_user')
    def test_create_account_with_management_permission(self, mock_create_user):
        """Test la création d'un compte par un utilisateur avec les droits de gestion"""
        # Simuler un utilisateur de gestion
        management_user = MagicMock()
        management_user.get_permission = Permissions.MANAGEMENT_TEAM
        
        # Simuler la création d'un compte commercial
        mock_create_user.return_value = {
            "name": "NewCommercial",
            "mail": "new@commercial.com",
            "phone": "123456789",
            "password": "password123",
            "role": 2  # Commercial
        }
        
        with patch.object(User, 'create_user') as mock_user_create:
            Controller.create_account(management_user)
            
            # Vérifier que l'utilisateur est créé avec le bon rôle
            mock_user_create.assert_called_once()
            args, kwargs = mock_user_create.call_args
            self.assertEqual(args[0]['role'], UserRole.COMMERCIAL.value)
    
    @patch('builtins.print')
    def test_show_all_data(self, mock_print):
        """Test l'affichage de tous les contrats et événements"""
        # Utiliser les contrats et événements créés dans setUp
        contracts = Contract.select()
        
        with patch('views.tabulate') as mock_tabulate:
            mock_tabulate.return_value = "Table formatée"
            Views.show_all_data(contracts)
            
            # Vérifier que tabulate a été appelé
            mock_tabulate.assert_called_once()
            # Vérifier que le résultat est affiché
            mock_print.assert_called_with("Table formatée")

    @patch('builtins.print')
    def test_show_unsupported_events(self, mock_print):
        """Test l'affichage des événements sans support"""
        # Utiliser l'événement créé dans setUp
        events = Event.select().where(Event.logistic_contact.is_null())
        
        with patch('views.tabulate') as mock_tabulate:
            mock_tabulate.return_value = "Table formatée"
            Views.show_unsupported_events(events)
            
            # Vérifier que tabulate a été appelé
            mock_tabulate.assert_called_once()
            # Vérifier que le résultat est affiché
            mock_print.assert_called_with("Table formatée")

    @patch('builtins.input')
    def test_select_client_update(self, mock_input):
        """Test la sélection du type de mise à jour client"""
        mock_input.return_value = "1"
        
        with patch('builtins.print'):
            choice = Views.select_client_update()
            
            # Vérifier que le bon choix est retourné
            self.assertEqual(choice, 1)
            # Vérifier que input a été appelé
            mock_input.assert_called_once()

    @patch('builtins.input')
    def test_update_client_phone(self, mock_input):
        """Test la mise à jour du téléphone d'un client"""
        mock_input.return_value = "9876543210"
        
        new_phone = Views.update_client_phone()
        
        # Vérifier que le bon numéro est retourné
        self.assertEqual(new_phone, "9876543210")
        # Vérifier que input a été appelé
        mock_input.assert_called_once()


    @patch('builtins.print')
    @patch('builtins.input')
    def test_remind_me(self, mock_input, mock_print):
        """Test la fonctionnalité de mémorisation de session"""
        mock_input.return_value = "1"
        
        result = Views.remind_me()
        
        # Vérifier que le bon choix est retourné
        self.assertEqual(result, 1)
        # Vérifier que input a été appelé avec le bon message
        mock_input.assert_called_once()

    @patch('builtins.print')
    def test_show_unsigned_contracts(self, mock_print):
        """Test l'affichage des contrats non signés"""
        # Créer un contrat non signé pour le test
        unsigned_contract = Contract.create(
            client=self.client,
            commercial=self.commercial_user,
            total_amount=1500,
            rest_amount=1500,
            state="En attente"
        )
        
        contracts = Contract.select().where(Contract.state != "Signé")
        
        with patch('views.tabulate') as mock_tabulate:
            mock_tabulate.return_value = "Table formatée"
            Views.show_unsigned_contracts(contracts)
            
            # Vérifier que tabulate a été appelé
            mock_tabulate.assert_called_once()
            # Vérifier que le résultat est affiché
            mock_print.assert_called_with("Table formatée")

    @patch('builtins.print')
    @patch('builtins.input')
    def test_update_contract_state(self, mock_input, mock_print):
        """Test la mise à jour de l'état d'un contrat"""
        mock_input.return_value = "2"  # Choisir "Signé"
        
        with patch('colors.Colors.highlight'), patch('colors.Colors.prompt'):
            new_state = Views.update_contract_state()
            
            # Vérifier que le bon état est retourné
            self.assertEqual(new_state, "Signé")
            # Vérifier que input a été appelé
            mock_input.assert_called_once()

if __name__ == '__main__':
    unittest.main()