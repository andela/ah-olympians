from django.shortcuts import reverse
import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status

from ..models import User


class Test_Registration_Error_Msgs(APITestCase):
    """ Class tests for custom error messages during registration."""
    client = APIClient()

    def setUp(self):
        """ Creates dummy user and user dictionary for testing."""
        self.dummy_user = User(email="mwangi@olympians.com",
                               username="ah-olympians", password="mwangi123")
        self.dummy_user.save()
        self.user = {
            "user": {
                "email": "mwangi@olympians.com",
                "username": "different",
                "password": "mwangi123"
            }
        }

    def test_existing_email(self):
        """ Tests error message when a new user provides existing email."""
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)
        email_result = result["errors"]["email"][0]

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(email_result, "Email is already registered to another user")

    def test_invalid_email(self):
        """ Tests error message when a new user provides invalid email."""
        self.user["user"]["email"] = "mwangi_olympians.com"
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)
        email_result = result["errors"]["email"][0]

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(email_result, "The provided email is invalid")

    def test_empty_or_email(self):
        """ Tests error message when a new user does not provide an email."""
        self.user["user"]["email"] = ""
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)
        email_result = result["errors"]["email"][0]

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(email_result, "Email must be provided to complete registration")

    def test_existing_username(self):
        """ Tests error message when a new user provides existing username."""
        self.user["user"]["username"] = "ah-olympians"
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)
        username_result = result["errors"]["username"][0]

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(username_result, "Username is already assigned to another user")

    def test_empty_username(self):
        """ Tests error message when a new user does not provide a username."""
        self.user["user"]["username"] = ""
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)
        username_result = result["errors"]["username"][0]

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(username_result, "A username is required to complete registration")

    def test_empty_password(self):
        """ Tests error message when new user does not provide a password."""
        self.user["user"]["password"] = ""
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)
        password_result = result["errors"]["password"][0]

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(password_result, "A password is required to complete registration")

    def test_short_password(self):
        """ Tests error message when password is less than 8 characters."""
        self.user["user"]["password"] = "abcd"
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)
        password_result = result["errors"]["password"][0]

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(password_result, "Please ensure that your password has more than 8 characters")

    def test_alphanumeric_password(self):
        """ Tests error message when password contains non-alphanumeric characters"""
        self.user["user"]["password"] = "abcd$"
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)
        password_result = result["errors"]["password"][0]

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(password_result, "Only numbers and letters are allowed in password")
