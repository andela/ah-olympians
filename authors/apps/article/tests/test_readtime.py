import json

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status


class TestArticleReadTime(APITestCase):
    """
    Class tests for article .
    """
    client = APIClient()

    def setUp(self):
        """ Creates user  and user dictionary for testing."""
        self.article = {
            "title": "Andela",
            "description": "sdsd",
            "body": "dsd",
            "images": ""
        }
        self.user = {
            "user": {
                "email": "chirchir@olympians.com",
                "username": "chirchir",
                "password": "test1234"
            }
        }
        create_user = self.client.post(
            '/api/users/', self.user, format='json')

        self.request_tkn = self.client.post(
            '/api/users/login/', self.user, format='json')

        token_request = json.loads(self.request_tkn.content)
        self.token = token_request["user"]["token"]

        create_profile = self.client.post('/api/profile/create_profile/', self.user,
                                          HTTP_AUTHORIZATION='Token ' + self.token,
                                          format='json')

    def test_view_readtime_one_article(self):
        """
        test to see one article
        :return:
        """
        token_request = json.loads(self.request_tkn.content)
        token = token_request["user"]["token"]
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)
        slug = result["article"]["slug"]

        response_article = self.client.get('/api/articles/' + slug,
                                           HTTP_AUTHORIZATION='Token ' + self.token,
                                           format='json')
        article = json.loads(response_article.content)

        self.assertIn(
            'read_time', str(result))
        self.assertEqual(response_article.status_code, status.HTTP_200_OK)
