"""Test API endpoints"""
import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ...authentication.models import User


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
            "images": ""
        }

        self.comment = {
            "comment": {
                "body": "His name was my name too."
            }
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

    def test_create_comment(self):
        """
        test create comment
        """
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["comment"]["body"],
                         "His name was my name too.")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_subcomment_of_comment(self):
        """
        test create comment
        """
        # create comment
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        # create subcomment of comment
        response = self.client.post(
            '/api/articles/andela/comments/' + str(result["comment"]["id"]) + "/subcomment", self.comment, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["comment"]["body"],
                         "His name was my name too.")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_comment_non_existing_article(self):
        """
        test create comment
        """
        response = self.client.post(
            '/api/articles/ndela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["comment"]["error"], "Article does not exist!")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_comment_non_existing_profile(self):
        """
        test create comment
        """
        # create user
        self.user['user']['email'] = "james@gmail.com"
        self.user['user']['username'] = "james"
        self.user['user']['password'] = "4567890123"
        self.client.post('/api/users/', self.user, format='json')
        # user login
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        # create comment
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["comment"]["error"],
                         "Permission denied! You don't have a profile")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_article_comments(self):
        """
        test get comments
        """
        # create article comments
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')

        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')

        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')

        # get article comments
        response = self.client.get(
            '/api/articles/andela/comments/', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["commentsCount"], 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comment(self):
        """
        test get comment
        """
        # create article comment
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        # get comment
        response = self.client.get(
            '/api/articles/andela/comments/' + str(result["comment"]["id"]), format='json')
        result = json.loads(response.content)

        self.assertEqual(result["comment"]["body"],
                         "His name was my name too.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_subcomment_of_comment(self):
        """
        test get comment
        """
        # create article comment
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        main_comment = str(result["comment"]["id"])

        # create subcomment of comment
        response = self.client.post(
            '/api/articles/andela/comments/' + main_comment + "/subcomment", self.comment, format='json')
        result = json.loads(response.content)

        # get sub comments
        response = self.client.get(
            '/api/articles/andela/comments/' + main_comment + "/subcomment", format='json')
        result = json.loads(response.content)

        self.assertEqual(result["commentsCount"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_non_existing_comment(self):
        """
        test get comment
        """
        response = self.client.get(
            '/api/articles/andela/comments/350', format='json')
        result = json.loads(response.content)

        self.assertEqual(result["comment"]["error"], "comment does not exist!")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_comment(self):
        """
        test get comment
        """
        # create article comment
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        # edit comment
        self.comment['comment']['body'] = "am edited"
        response = self.client.put(
            '/api/articles/andela/comments/' + str(result["comment"]["id"]), self.comment, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["comment"]["body"], "am edited")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_comment(self):
        """
        test delete comment
        """
        # create article comment
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        # delete comment
        response = self.client.delete(
            '/api/articles/andela/comments/' + str(result["comment"]["id"]), format='json')

        self.assertEqual(response.data["message"],
                         "comment deleted successfully")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_edit_other_persons_comment(self):
        """
        test edit comment
        """
        # create article comment
        response = self.client.post(
            '/api/articles/andela/comments/', self.comment, format='json')
        result = json.loads(response.content)

        edit_comment = str(result["comment"]["id"])

        # create user
        self.user['user']['email'] = "james@gmail.com"
        self.user['user']['username'] = "james"
        self.user['user']['password'] = "4567890123"
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

        # edit comment
        self.comment['comment']['body'] = "am edited"
        response = self.client.put(
            '/api/articles/andela/comments/' + edit_comment, self.comment, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["comment"]["error"],
                         "You do not have that permission on this comment!")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
