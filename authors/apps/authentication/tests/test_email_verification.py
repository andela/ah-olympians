from django.shortcuts import reverse
import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status

from ..models import EmailVerification, User


class TestEmailVerification(APITestCase):
    """
    Class tests for email verification .
    """
    client = APIClient()

    def setUp(self):
        """ Creates user  and user dictionary for testing."""
        self.user = {
            "user": {
                "email": "chirchir@olympians.com",
                "username": "chirchir",
                "password": "test1234"
            }
        }

    def test_success_verification(self):
        """ Tests the token is created and saved on the db."""
        response = self.client.post('/api/users/', self.user, format='json')
        self.assertEqual(EmailVerification.objects.count(), 1)

    def test_token_verified(self):
        """
        tests the token is verified and used
        """
        self.client.post('/api/users/', self.user, format='json')
        user1 = User.objects.get(username ='chirchir')
        verification = EmailVerification.objects.filter(user=user1).first()
        token = verification.token
        token_verify = {"token": token}
        response = self.client.post('/api/users/verify/', token_verify, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["user"]["success"], "valid token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_already_used(self):
        """
        tests for an already used token by sending multiple tests
        """
        self.client.post('/api/users/', self.user, format='json')
        user1 = User.objects.get(username='chirchir')
        verification = EmailVerification.objects.filter(user=user1).first()
        token = verification.token
        token_verify = {"token": token}
        self.client.post('/api/users/verify/', token_verify, format='json')
        response = self.client.post('/api/users/verify/', token_verify, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["user"]["error"], "Token already used")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_doesnt_exist(self):
        """
        Tests for a non existing token
        """
        self.client.post('/api/users/', self.user, format='json')
        user1 = User.objects.get(username='chirchir')
        verification = EmailVerification.objects.filter(user=user1).first()
        token_verify = {"token": "test"}
        response = self.client.post('/api/users/verify/', token_verify, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["user"]["error"], "invalid token")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
