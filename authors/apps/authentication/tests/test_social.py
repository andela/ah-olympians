import json
import os

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

access_token = os.environ['FB_ACCESS_TOKEN']
twitter_access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']
google_token = os.environ['GOOGLE_ACCESS_TOKEN']
access_token_secret = ''



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
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    
    def test_user_is_authenticated_twitter(self):
        '''
          test if a user is authenticated via twitter that requires an access token secret 
          '''
        token = {
              "access_token":twitter_access_token,
              "access_token_secret":twitter_access_token_secret,
              "provider":"twitter"
          }

        response = self.client.post(
              reverse("authentication:login_social"),
              token,
              format='json'
          )

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    
    def test_google_signin(self):
        '''
            test when a  user signins using google
        '''

        token = {
            "access_token":google_token,
            "provider":"google-oauth2",
            "access_token_secret":""
        }

        repsonse = self.client.post(
            reverse("authentication:login_social"),
            token,
            format='json'
        )
        self.assertEqual(repsonse.status_code,status.HTTP_201_CREATED)
