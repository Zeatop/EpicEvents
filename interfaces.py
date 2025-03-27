from abc import ABC, abstractmethod

class AuthenticationInterface(ABC):
    @abstractmethod
    def authenticate(self, credentials: dict) -> bool:
        """Authentifie un utilisateur avec les identifiants fournis"""
        pass
    
    @abstractmethod
    def verify_session(self) -> bool:
        """Vérifie si la session en cours est valide"""
        pass