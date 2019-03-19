import json

from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status


class TestArticleLikes(APITestCase):
    """ This class tests the Article like and dislike feature
    """

    client = APIClient()

    def setUp(self):
        """ This is the set-up method for all tests
        """
        self.user = {"user": {
            "username": "kibet",
            "email": "kibet@olympians.com",
            "password": "qwerty12"
        }}

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

        # create user
        self.client.post(
            '/api/users/', self.user, format='json')

        response = self.client.post(
            '/api/users/login/', self.user, format='json')

        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        profile = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        prof_result = json.loads(profile.content)

        article = self.client.post('/api/articles/', self.article,
                                   format='json')
                                   
        article_result = json.loads(article.content)
        self.slug = article_result["article"]["slug"]

    def test_like_article(self):
        """
        Test like an article
        """
        #
        response = self.client.post('/api/articles/' + self.slug + '/like',
                                    format='json')
        result = json.loads(response.content)
        print(response.content)

        self.assertIn('Successfully liked: {} article'.format(self.slug),
                      str(result))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_dislike_article(self):
        """
        Test like an article
        """
        #
        response = self.client.post('/api/articles/' + self.slug + '/dislike',
                                    format='json')
        result = json.loads(response.content)

        self.assertIn('Successfully disliked: {} article'.format(self.slug),
                      str(result))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_non_existing_article(self):
        """
        Test like an article
        """
        #
        response = self.client.post('/api/articles/random/like',
                                    format='json')
        result = json.loads(response.content)

        self.assertIn('Article requested does not exist'.format(self.slug),
                      str(result))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unlike_article(self):
        """
        Test like an article
        """
        #
        self.client.post('/api/articles/' + self.slug + '/like',
                         format='json')
        response = self.client.post('/api/articles/' + self.slug + '/like',
                                    format='json')
        result = json.loads(response.content)

        self.assertIn('Successfully undid (dis)like on {} article'.format(self.slug),
                      str(result))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
