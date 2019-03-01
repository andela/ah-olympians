import json

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


access_token = "EAAFhpUjDw2sBADzjtoq6C0KhOdsFyB2b9lkj7pJqNqPrOTgMSAPfHUh9ZBbhi2naHxItdnIasTcYOzSvNkWZCLDKmEvTrZBgCyOZA1sx25bwyHc8LpfkfahiI70NgHQEuwXmjZBu96ZBaQrUL5PrUZBDMSgeWciGPzwGC6IZAVqnh3IvVV8ZA7VkYEoCF6Fo1cBt2kLTS7qonMAHKOxErcLbo"
access_token_secret=""

class SocialLoginTest(APITestCase):
    """ 
    Social Login Test  functionality of loging in using social authentication
    """

    def test_provide_access_token_to_login(self):

        token = {
            "access_token":"",
            "provider":"facebook"
        }

        response = self.client.post(
            reverse("authentication:login_social"),
            token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_lacking_provider(self):
        
        ''' test if provider is provided '''

        token = {
            "access_token":access_token,
            "provider":""
        }

        response = self.client.post(
            reverse("authentication:login_social"),
            token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_user_is_authenticated(self):

        ''' test if a user is authenticated '''

        token = {
            "access_token":access_token,
            "access_token_secret":access_token_secret,
            "provider":"facebook"
        }

        response = self.client.post(
            reverse("authentication:login_social"),
            token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)