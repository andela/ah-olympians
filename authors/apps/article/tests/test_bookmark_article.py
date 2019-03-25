"""Test API endpoints"""
import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ...authentication.models import User


class CommentsTest(APITestCase):
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

        self.article = {
            "title": "Andela",
            "description": "sdsd",
            "body": "dsd",
            "images": "",
            "tag_list": ['kelvin', 'onkundi']
        }
        # create user
        self.client.post('/api/users/', self.user, format='json')
        # user login
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        # create profile
        self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')

        # create article
        response = self.client.post(
            '/api/articles/', self.article, format='json')

    def test_bookmark_article(self):
        """
        test bookmark article
        """
        response = self.client.post(
            '/api/articles/andela/bookmark', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"],
                         "Bookmark created")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_bookmark_bookmarked_article(self):
        """
        test bookmark an article already bookmarked
        """
        # bookmark article
        response = self.client.post(
            '/api/articles/andela/bookmark', format='json')

        # bookmark article again
        response = self.client.post(
            '/api/articles/andela/bookmark', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["error"],
                         "Bookmark already exists")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_bookmark(self):
        """
        test remove bookmark
        """
        # bookmark article
        response = self.client.post(
            '/api/articles/andela/bookmark', format='json')

        # remove bookmark
        response = self.client.delete(
            '/api/articles/andela/bookmark', format='json')

        self.assertEqual(response.data["message"],
                         "Bookmark removed")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_remove_nonexising_bookmark(self):
        """
        test remove bookmark that does not exist
        """
        # remove bookmark
        response = self.client.delete(
            '/api/articles/andela/bookmark', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["error"],
                         "Bookmark does not exist")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_bookmarks(self):
        """
        test get all user bookmarks
        """
        # bookmark article
        response = self.client.post(
            '/api/articles/andela/bookmark', format='json')

        # get bookmarks
        response = self.client.get('/api/bookmarks/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["articlesCount"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
