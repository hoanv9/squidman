from app.models.user import User

class AuthService:
    @staticmethod
    def login(username, password):
        """
        Authenticate a user by username and password.
        Returns User object if successful, None otherwise.
        """
        # Logic delegate to User model (which handles Linux/Dev auth)
        return User.authenticate(username, password)
