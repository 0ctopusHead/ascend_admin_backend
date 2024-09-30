from flask import request, redirect, jsonify
import requests
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()
REDIRECT_URI = 'http://admin.ascendedu.systems/'
AUTH_ENDPOINT = 'https://oauth.cmu.ac.th/v1/Authorize.aspx'
TOKEN_ENDPOINT = 'https://oauth.cmu.ac.th/v1/GetToken.aspx'
USERINFO_ENDPOINT = 'https://misapi.cmu.ac.th/cmuitaccount/v1/api/cmuitaccount/basicinfo'
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
CLIENT_ID = "C9VKwSmXsTJUYgheHucA0MwUQnz7QPu0XMKYy04H"

class AuthenticationService:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.redirect_uri = REDIRECT_URI


    def login(self):
        login_url = f'{AUTH_ENDPOINT}?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope=cmuitaccount.basicinfo'
        return login_url, 200

    def callback(self):
        code = request.form.get('code')
        print("Form data received:", request.form)

        if not code:
            print("Authorization code is missing.")
            return jsonify({'error': 'Authorization code is missing'}), 400

        print("Received authorization code:", code)
        data = {
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'authorization_code'
        }

        response = requests.post(TOKEN_ENDPOINT, data=data)
        if response.status_code == 200:
            print("Access token response:", response.json())
            return jsonify(response.json())
        else:
            print("Failed to retrieve access token:", response.text)
            return jsonify({'error': 'Failed to retrieve access token'}), 400


    def user_info(self):
        access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        print(access_token)
        if not access_token:
            return 'Access token not provided.', 401

        userinfo_endpoint = 'https://misapi.cmu.ac.th/cmuitaccount/v1/api/cmuitaccount/basicinfo'

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }

        response = requests.get(userinfo_endpoint, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(user_info)
            return jsonify(user_info),200
        else:
            raise FileNotFoundError("Failed to fetch user information due to invalid access token.")

    def get_access_token(self):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',  # Specify the correct grant type
            'scope': 'cmuitaccount.basicinfo'
        }

        try:
            response = requests.post(TOKEN_ENDPOINT, data=data)
            response.raise_for_status()  # Raises an error for non-200 responses
            response_data = response.json()
            logger.info(f"Access token retrieved: {response_data.get('access_token')}")
            return response_data.get('access_token')
        except requests.RequestException as e:
            logger.error(f"Error retrieving access token: {str(e)}")
            return None