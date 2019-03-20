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
        create_user = self.client.post(
            '/api/users/', self.user, format='json')

        self.request_tkn = self.client.post(
            '/api/users/login/', self.user, format='json')

        token_request = json.loads(self.request_tkn.content)
        self.token = token_request["user"]["token"]

        create_profile = self.client.post('/api/profile/create_profile/', self.user,
                                          HTTP_AUTHORIZATION='Token ' + self.token,
                                          format='json')

    def test_successful_favorite(self):
        """Tests a request for succesfull favoriting an article
        :return:
        """
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)
        slug = result["article"]["slug"]

        response_article = self.client.post('/api/articles/' + slug + '/favorite',
                                            HTTP_AUTHORIZATION='Token ' + self.token,
                                            format='json')
        article = json.loads(response_article.content)

        self.assertIn(
            'Successfully favourited the article', str(article))
        self.assertEqual(response_article.status_code, status.HTTP_202_ACCEPTED)

    def test_double_favorite(self):
        """Tests a request for succesfull favoriting an article twice
            :return:
        """
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)
        slug = result["article"]["slug"]

        self.client.post('/api/articles/' + slug + '/favorite',
                        HTTP_AUTHORIZATION='Token ' + self.token,
                        format='json')

        response_article = self.client.post('/api/articles/' + slug + '/favorite',
                                            HTTP_AUTHORIZATION='Token ' + self.token,
                                            format='json')
        article = json.loads(response_article.content)

        self.assertIn(
            'you have already favourited the article', str(article))
        self.assertEqual(response_article.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_favorite_unexisting_article(self):
        """
        test if slug is created in every instance
        :return:
        """
        response_article = self.client.post('/api/articles/test/favorite',
                                            HTTP_AUTHORIZATION='Token ' + self.token,
                                            format='json')
        article = json.loads(response_article.content)

        self.assertIn(
            "You can not favourite this article because it doesn't exist", str(article))
        self.assertEqual(response_article.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_favorite(self):
        """Tests a request for succesfull favoriting an article
        :return:
        """
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)
        slug = result["article"]["slug"]
        self.client.post('/api/articles/' + slug + '/favorite',
                         HTTP_AUTHORIZATION='Token ' + self.token,
                         format='json')

        response_article = self.client.delete('/api/articles/' + slug + '/favorite',
                                              HTTP_AUTHORIZATION='Token ' + self.token,
                                              format='json')
        article = json.loads(response_article.content)

        self.assertIn(
            'you have successfully deleted', str(article))
        self.assertEqual(response_article.status_code, status.HTTP_202_ACCEPTED)

    def test_double_delete_favorite(self):
        """Tests a request for succesfull favoriting an article twice
            :return:
        """
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)
        slug = result["article"]["slug"]

        self.client.post('/api/articles/' + slug + '/favorite',
                         HTTP_AUTHORIZATION='Token ' + self.token,
                         format='json')

        self.client.delete('/api/articles/' + slug + '/favorite',
                           HTTP_AUTHORIZATION='Token ' + self.token,
                           format='json')

        response_article = self.client.delete('/api/articles/' + slug + '/favorite',
                                              HTTP_AUTHORIZATION='Token ' + self.token,
                                              format='json')
        article = json.loads(response_article.content)

        self.assertIn(
            'you have not favourited this article', str(article))
        self.assertEqual(response_article.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_delete_favorite_unexisting_article(self):
        """
        test if slug is created in every instance
        :return:
        """
        response_article = self.client.delete('/api/articles/test/favorite',
                                              HTTP_AUTHORIZATION='Token ' + self.token,
                                              format='json')
        article = json.loads(response_article.content)

        self.assertIn(
            "You can not favourite this article", str(article))
        self.assertEqual(response_article.status_code, status.HTTP_404_NOT_FOUND)
