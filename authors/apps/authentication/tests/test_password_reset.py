import json

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status

from ..models import PasswordTokenReset, User


class TestPasswordResetRequest(APITestCase):
    """
    Class tests for email verification .
    """
    client = APIClient()

    def setUp(self):
        """ Creates user  and user dictionary for testing."""
        self.user = {"user": {
            "username": "kibet",
            "email": "kibet@olympians.com",
            "password": "qwerty12"
        }}
        self.user_email = {'email': 'kibet@olympians.com'}
        self.non_user_email = {'email': 'non_user@email.com'}
        self.invalid_email = {'email': 'email.email.com'}
        self.empty_email = {'email': ''}
        self.blank_email = {}
        self.invalid_token = 1
        self.expired_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.' \
                             'eyJpZCI6MSwiZXhwIjoxNTUxNTE5MjYzfQ.' \
                             'i9NpH8R1R3S7kCAg0GiPjknTZvLnUElRU6vKXN773EA'

        self.short_password = {"password": "Pass"}
        self.empty_password = {"password": ""}
        self.blank_password = {}
        self.valid_password = {"password": "Passw0rd"}

        create_user = self.client.post(
            '/api/users/', self.user, format='json')

        request_tkn = self.client.post(
            '/api/users/reset_password/', self.user_email, format='json')

    def test_existing_user(self):
        """Tests a request which belongs to a valid user
        :return:
        """
        response = self.client.post(
            '/api/users/reset_password/', self.user_email, format='json')
        result = json.loads(response.content)

        self.assertIn('If we found an account;', str(result))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_too_many_request(self):
        """Tests a request which belongs to a valid user
        :return:
        """
        for i in range(5):
            response = self.client.post(
                '/api/users/reset_password/', self.user_email, format='json')
        result = json.loads(response.content)

        self.assertIn('Too many password requests made in the last 24 hrs.',
                      str(result))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_non_user(self):
        """Tests a request which belongs to a non user
        :return:
        """
        response = self.client.post(
            '/api/users/reset_password/', self.non_user_email, format='json')
        result = json.loads(response.content)

        self.assertIn('If we found an account;', str(result))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_email(self):
        """Tests a request with invalid email
        :return:
        """
        response = self.client.post(
            '/api/users/reset_password/', self.invalid_email, format='json')
        result = json.loads(response.content)

        self.assertIn('Enter a valid email address.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_string(self):
        """Tests a request with an empty string as email
        :return:
        """
        response = self.client.post(
            '/api/users/reset_password/', self.empty_email, format='json')
        result = json.loads(response.content)

        self.assertIn('This field may not be blank.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_request(self):
        """Tests a blank request
        :return:
        """
        response = self.client.post(
            '/api/users/reset_password/', self.blank_email, format='json')
        result = json.loads(response.content)

        self.assertIn('This field is required.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test for setting new email
    def test_short_password(self):
        """Test for a password less that 8 characters"""
        user = User.objects.get(email='kibet@olympians.com')
        valid_token = PasswordTokenReset.objects.get(user_id=user.id)
        response = self.client.put(
            '/api/users/reset_password/' + valid_token.token,
            self.short_password,
            format='json')
        result = json.loads(response.content)

        self.assertIn('Ensure this field has at least 8 characters.',
                      str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_password(self):
        """Test for an empty password"""
        user = User.objects.get(email='kibet@olympians.com')
        valid_token = PasswordTokenReset.objects.get(user_id=user.id)
        response = self.client.put(
            '/api/users/reset_password/' + valid_token.token,
            self.empty_password,
            format='json')
        result = json.loads(response.content)

        self.assertIn('This field may not be blank.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_password(self):
        """Test for a blank password"""
        user = User.objects.get(email='kibet@olympians.com')
        valid_token = PasswordTokenReset.objects.get(user_id=user.id)
        response = self.client.put(
            '/api/users/reset_password/' + valid_token.token,
            self.blank_password,
            format='json')
        result = json.loads(response.content)

        self.assertIn('This field is required.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_password(self):
        """Test for a valid password"""
        user = User.objects.get(email='kibet@olympians.com')
        valid_token = PasswordTokenReset.objects.get(user_id=user.id)
        response = self.client.put(
            '/api/users/reset_password/' + valid_token.token,
            self.valid_password,
            format='json')
        result = json.loads(response.content)

        self.assertIn('Password reset successful.', str(result))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
