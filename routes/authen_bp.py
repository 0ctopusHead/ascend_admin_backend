from flask import Blueprint, request
from controller.AuthenticationController import AuthenticationController

authen_bp = Blueprint('authen_bp', __name__)
authen_controller = AuthenticationController()

@authen_bp.route('/login', methods=['GET'])
def login():
    return authen_controller.login()
@authen_bp.route('/callback', methods=['POST'])
def callback():
    return authen_controller.callback()

@authen_bp.route('/user_info', methods=['GET'])
def user_info():
    return authen_controller.get_user_info()

@authen_bp.route('/get_token', methods=['GET'])
def get_token():
    token = authen_controller.get_access_token()
    return authen_controller.get_access_token()