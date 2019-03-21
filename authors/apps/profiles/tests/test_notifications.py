"""Test Notification Endpoint"""
import json
from rest_framework.exceptions import APIException
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ...authentication.models import User
from ...article.models import Article
from ..models import UserProfile

# tests for Endpoint


class NotificationTest(APITestCase):
    """ Test for notifications endpoint."""

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

        self.profile = {
            "bio": "am fantastic",
            "interests": "football",
            "favorite_quote": "Yes we can",
            "mailing_address": "P.O BOX 1080",
            "website": "http://www.web.com",
            "active_profile": True
        }

        self.user2 = {
            "user": {
                "email": "notcaro@yahoo.com",
                "username": "notcaro",
                "password": "07921513542"
            }
        }

        self.profile2 = {
            "bio": "am fantastic",
            "interests": "notfootball",
            "favorite_quote": "Yes we can",
            "mailing_address": "P.O BOX 1080",
            "website": "http://www.web.com",
            "active_profile": True
        }

        self.user3 = {
            "user": {
                "email": "a_user@yahoo.com",
                "username": "newuser",
                "password": "07921513542"
            }
        }

        self.article = {
            "title": "Andela",
            "description": "sdsd",
            "body": "dsd",
            "images": "",
            "tag_list": ['kelvin', 'novak']
        }

        self.comment = {"comment":{"body": "A comment"}}

        # create user 1
        self.client.post('/api/users/', self.user, format='json')
        # user 1 login
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])
        # Create user 1 profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        # create user 3
        self.client.post('/api/users/', self.user3, format='json')

        # create user 2
        self.client.post('/api/users/', self.user2, format='json')
        # user 2 login
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)


        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        # Create user 2 profile
        self.client.post(
            '/api/profile/create_profile/', self.profile2, format='json')

        self.client.put('/api/profile/view_profile/app_notifications/')

        # User 2 follow User 1
        user1 = User.objects.get(username='caro')
        response = self.client.post(
            '/api/profile/view_profile/' + str(user1.id) + '/follow/', format='json')

    def test_new_article_notification(self):
        """
        Test if user gets notification if author he/she follows posts new article
        """
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        self.client.post(
            '/api/articles/', self.article, format='json')

        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        response = self.client.get(
            '/api/profile/view_profile/notifications/')
        result = json.loads(response.content)

        self.assertIn("A new arti", str(result["notifications"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_new_comment_notification(self):
        """
        Test if user gets notification if article he/she follows gets new comment
        """
        # User 1 creates new article
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        self.client.post(
            '/api/articles/', self.article, format='json')

        # User 2 favorites article
        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        slug = Article.objects.get(title='Andela').slug

        self.client.post(
            '/api/articles/' + str(slug) + '/favorite', format='json')

        response = self.client.post(
            '/api/articles/' + str(slug) + '/comments/', self.comment, format='json')

        response = self.client.get(
            '/api/profile/view_profile/notifications/')
        result = json.loads(response.content)

        self.assertIn("A new comm", str(result["notifications"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_set_false(self):
        """
        Test if status message when user has deactivated in-app notifications
        """
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        self.client.post(
            '/api/articles/', self.article, format='json')

        response = self.client.post(
            '/api/users/login/', self.user2, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        self.client.put('/api/profile/view_profile/app_notifications/')

        response = self.client.get(
            '/api/profile/view_profile/notifications/')
        result = json.loads(response.content)

        self.assertEqual(result["notifications"]["message"],
            "You have disabled in-app notifications. Please enable to view")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_opt_out_app_notifs(self):
        """ Test user opting out of in-app notifications."""
        response = self.client.put(
            '/api/profile/view_profile/app_notifications/')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["in_app_notify"], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_opt_in_app_notifs(self):
        """ Test user opting in for in-app notifications."""
        self.client.put(
            '/api/profile/view_profile/app_notifications/')
        response = self.client.put(
            '/api/profile/view_profile/app_notifications/')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["in_app_notify"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_opt_in_app_notifs_without_profile(self):
        """
        Test user opting in for in-app notifications without creating a profile.
        """
        response = self.client.post(
            '/api/users/login/', self.user3, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        response = self.client.put('/api/profile/view_profile/app_notifications/')
        result = json.loads(response.content)

        self.assertEqual('User has no profile', result["profile"]["message"])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_opt_in_email_notifs_without_profile(self):
        """
        Test user opting in for in-app notifications without creating a profile.
        """
        response = self.client.post(
            '/api/users/login/', self.user3, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        response = self.client.put('/api/profile/view_profile/email_notifications/')
        result = json.loads(response.content)

        self.assertEqual('User has no profile', result["profile"]["message"])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_opt_out_email_notifs(self):
        """ Test user opting out of email notifications."""
        response = self.client.put(
            '/api/profile/view_profile/email_notifications/')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["email_notify"], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_opt_in_email_notifs(self):
        """ Test user opting in for email notifications."""
        self.client.put(
            '/api/profile/view_profile/email_notifications/')
        response = self.client.put(
            '/api/profile/view_profile/email_notifications/')
        result = json.loads(response.content)

        self.assertEqual(result["profile"]["email_notify"], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)






