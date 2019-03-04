"""Test JWT authentication"""
import json
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ..models import User


class UserTest(APITestCase):
    client = APIClient()

    def setUp(self):
        # add test data
        self.user = {
            "user": {
                "email": "caro@yahoo.com",
                "username": "caro",
                "password": "07921513542"
            }
        }

        self.headers = {"Authorization": ""}

    def _generate_jwt_token(self, user_id):
        """
        Generates a JSON Web Token
        """
        token_dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': user_id,
            'exp': int(token_dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    def test_login_user_JWT_genaration(self):
        """
        test login
        """
        # create user
        response = self.client.post('/api/users/', self.user, format='json')
        # hit the API endpoint
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.assertIn('token', str(result))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_with_JWT(self):
        """
        test retrieve user with JWT
        """
        # create user
        response = self.client.post('/api/users/', self.user, format='json')
        # Login user
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        # Retrieve user
        response = self.client.get('/api/user/', format='json')
        result = json.loads(response.content)
        self.assertEqual(result["user"]["email"], "caro@yahoo.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_with_invalid_user(self):
        """
        test retrieve user with a non existent user
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self._generate_jwt_token(100))

        # Retrieve user
        response = self.client.get('/api/user/', format='json')
        result = json.loads(response.content)
        self.assertEqual(result["user"]["detail"],
                         "No user matching this token was found.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_with_invalid_token(self):
        """
        test retrieve user with invalid acces token
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNTUxNjg0ODE4fQ.koXGJ_hLzkIsMbzuvjZtsFAAjJ9BOSs6yVHLzQgVItA')

        # Retrieve user
        response = self.client.get('/api/user/', format='json')
        result = json.loads(response.content)
        self.assertEqual(result["user"]["detail"],
                         "Invalid authentication. Could not decode token.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_with_invalid_token_prefix(self):
        """
        test retrieve user with invalid token prefix
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNTUxNjg0ODE4fQ.koXGJ_hLzkIsMbzuvjZtsFAAjJ9BOSs6yVHLzQgVItA')

        # Retrieve user
        response = self.client.get('/api/user/', format='json')
        result = json.loads(response.content)
        self.assertEqual(result["user"]["detail"],
                         "Authentication credentials were not provided.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_with_no_token_prefix(self):
        """
        test retrieve user with no token prefix
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNTUxNjg0ODE4fQ.koXGJ_hLzkIsMbzuvjZtsFAAjJ9BOSs6yVHLzQgVItA')

        # Retrieve user
        response = self.client.get('/api/user/', format='json')
        result = json.loads(response.content)
        self.assertEqual(result["user"]["detail"],
                         "Authentication credentials were not provided.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_with_space_in_token(self):
        """
        test retrieve user with a space in access token
        """

        self.client.credentials(
            HTTP_AUTHORIZATION='Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZX hwIjoxNTUxNjg0ODE4fQ.koXGJ_hLzkIsMbzuvjZtsFAAjJ9BOSs6yVHLzQgVItA')

        # Retrieve user
        response = self.client.get('/api/user/', format='json')
        result = json.loads(response.content)
        self.assertEqual(result["user"]["detail"],
                         "Authentication credentials were not provided.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_with_inactive_user(self):
        """
        test retrieve user with JWT
        """
        # create user
        response = self.client.post('/api/users/', self.user, format='json')
        # Login user
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        # deactivate user
        current_user = User.objects.get(username='caro')
        current_user.is_active = False
        current_user.save()

        # Retrieve user
        response = self.client.get('/api/user/', format='json')
        result = json.loads(response.content)
        self.assertEqual(result["user"]["detail"],
                         "This user has been deactivated.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
