from service.AuthenticationService import AuthenticationService
class AuthenticationController:
    def __init__(self):
        self.auth_service = AuthenticationService()

    def login(self):
        return self.auth_service.login()

    def callback(self):
        return self.auth_service.callback()

    def get_user_info(self):
        return self.auth_service.user_info()

    def get_access_token(self):
        return self.auth_service.get_access_token()