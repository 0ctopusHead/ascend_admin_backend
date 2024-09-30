import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from service.AuthenticationService import AuthenticationService

class TestAdminAuthentication(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.auth_service = AuthenticationService()
        self.client = self.app.test_client()

        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()


    def get_mocked_user_info(self, username):
        return {
            "cmuitaccount": 'yada_la@cmu.ac.th',
            "firstname_EN": 'YADA'
        }

    @patch('requests.post')
    @patch('requests.get')
    def test_user_info_with_token(self, mock_get, mock_post):
        username = 'yada_la@cmu.ac.th'
        mock_get.return_value = MagicMock(status_code=200,
                                          json=MagicMock(return_value=self.get_mocked_user_info(username)))

        with self.app.test_request_context(headers={"Authorization": f"Bearer valid_access_token"}):
            response, status_code = self.auth_service.user_info()

            self.assertEqual(status_code, 200)
            self.assertEqual(response.json['firstname_EN'], 'YADA')


    @patch('requests.get')
    def test_get_user_info_failure_raises_file_not_found_error(self, mock_get):
        mock_get.return_value = MagicMock(
                                          json=MagicMock(return_value={"message": "Failed to fetch user information"}))

        with self.app.test_request_context(headers={"Authorization": "Bearer  "}):
            with self.assertRaises(FileNotFoundError):
                self.auth_service.user_info()


if __name__ == '__main__':
    unittest.main()
