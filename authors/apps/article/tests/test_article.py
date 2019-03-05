import json

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status


class TestArticle(APITestCase):
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
        self.article1 = {

            "description": "sdsd",
            "body": "dsd",
            "images": ""
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

    def test_successful_article(self):
        """Tests a request which belongs to a valid json file for article
        :return:
        """
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertIn(
            'Andela', str(result))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_title_article(self):
        """Tests a request which does not have a title on the json
                :return:
                """
        token_request = json.loads(self.request_tkn.content)
        token = token_request["user"]["token"]
        response = self.client.post('/api/articles/', self.article1,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertIn('This field is required.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_slug_article(self):
        """
        test if slug is created in every instance
        :return:
        """
        token_request = json.loads(self.request_tkn.content)
        token = token_request["user"]["token"]
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertIn(
            "andela", result["article"]["slug"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unique_slug_article(self):
        """
        create if slug is unique
        :return:
        """
        token_request = json.loads(self.request_tkn.content)
        token = token_request["user"]["token"]
        self.client.post('/api/articles/', self.article,
                         HTTP_AUTHORIZATION='Token ' + token,
                         format='json')
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(
            "andela-1", result["article"]["slug"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_view_all_articles(self):
        """
        test view all articles
        """
        self.client.post('/api/articles/', self.article,
                         HTTP_AUTHORIZATION='Token ' + self.token,
                         format='json')
        response = self.client.get(
            '/api/articles/',
            HTTP_AUTHORIZATION='Token ' + self.token,
            format='json')
        result = json.loads(response.content)
        self.assertEqual(1, len(result["articles"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_one_article(self):
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
            'Andela', str(result))
        self.assertEqual(response_article.status_code, status.HTTP_200_OK)

    def test_unexisting_article(self):
        """
        test to see one article
        :return:
        """

        response_article = self.client.get('/api/articles/test',
                                           HTTP_AUTHORIZATION='Token ' + self.token,
                                           format='json')
        article = json.loads(response_article.content)

        self.assertIn('The article requested does not exist', str(article))
        self.assertEqual(response_article.status_code, status.HTTP_404_NOT_FOUND)
