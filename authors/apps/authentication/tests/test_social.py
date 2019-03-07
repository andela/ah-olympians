import json
import os

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


twitter_access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']



class SocialLoginTest(APITestCase):
    """ 
    Social Login Test  functionality of loging in using social authentication
    """

    def test_provide_access_token_to_login(self):

        token = {
            "access_token":"",
            "access_token_secret":twitter_access_token_secret,
            "provider":"twitter"
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
            "access_token":twitter_access_token,
            "access_token_secret":twitter_access_token_secret,
            "provider":""
        }

        response = self.client.post(
            reverse("authentication:login_social"),
            token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_provide_all_credential_to_login(self):

        token = {
            "access_token":"",
            "access_token_secret":twitter_access_token_secret,
            "provider":"twitter"
        }

        response = self.client.post(
            reverse("authentication:login_social"),
            token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_provide_access_token_secret_to_login(self):
        '''
        test for a user must provide an access token  to login
        '''

        token = {
            "access_token":twitter_access_token,
            "access_token_secret":"",
            "provider":"twitter"
        }
        
        response = self.client.post(
            reverse("authentication:login_social"),
            token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

   