import json

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
import pdb


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
            "images": "",
            "tag_list":['kelvin','novak']
        }
        self.article0 = {
            "title": "Andela1",
            "description": "sdsd1",
            "body": "dsd1",
            "images": "",
            "tag_list":['kelvin','onkundi']
        }
        self.article2 = {
            "title": "Andela",
            "description": "sdsd",
            "body": "dsd",
            "images": "",
            "slug": "andela",
            "tag_list":['kelvin','onkundi']
        }
        self.user = {
            "user": {
                "email": "chirchir@olympians.com",
                "username": "chirchir",
                "password": "test1234"
            }
        }

        self.user2 = {
            "user": {
                "email": "chirch@olympians.com",
                "username": "chirch",
                "password": "test1234"
            }
        }

        self.article1 = {

            "description": "sdsd",
            "body": "dsd",
            "images": "",
            "tag_list":['kelvin','novak']

        }
        create_user = self.client.post(
            '/api/users/', self.user, format='json')

        create_user2 = self.client.post(
            '/api/users/', self.user2, format='json')

        self.request_tkn = self.client.post(
            '/api/users/login/', self.user, format='json')

        self.request_tkn2 = self.client.post(
            '/api/users/login/', self.user2, format='json')

        token_request = json.loads(self.request_tkn.content)
        self.token = token_request["user"]["token"]

        token_request2 = json.loads(self.request_tkn2.content)
        self.token2 = token_request2["user"]["token"]

        create_profile = self.client.post('/api/profile/create_profile/', self.user,
                                          HTTP_AUTHORIZATION='Token ' + self.token,
                                          format='json')

        create_profile2 = self.client.post('/api/profile/create_profile/', self.user2,
                                           HTTP_AUTHORIZATION='Token ' + self.token2,
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
        self.client.post('/api/articles/', self.article,
                         HTTP_AUTHORIZATION='Token ' + self.token,
                         format='json')
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(
            "andela-1", result["article"]["slug"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_same_slug(self):
        """
        tests the response if one creates a slug that is already in use
        :return:
        """
        self.client.post('/api/articles/', self.article2,
                         HTTP_AUTHORIZATION='Token ' + self.token,
                         format='json')
        response = self.client.post('/api/articles/', self.article2,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertIn('article with this slug already exists.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_delete_article(self):
       """
       test the delete method
       :return:
       """
       token_request = json.loads(self.request_tkn.content)
       token = token_request["user"]["token"]
       response = self.client.post('/api/articles/', self.article,
                                   HTTP_AUTHORIZATION='Token ' + self.token,
                                   format='json')
       result = json.loads(response.content)
       slug = result["article"]["slug"]

       response_article = self.client.delete('/api/articles/andela',
                                             HTTP_AUTHORIZATION='Token ' + self.token,
                                             format='json')
       article = json.loads(response_article.content)

       self.assertIn(
           'article deleted', str(article))
       self.assertEqual(response_article.status_code, status.HTTP_202_ACCEPTED)

    def test_delete_unexistting_article(self):
        """
        tests the delete for a un existing article
        :return:
        """
        response_article = self.client.delete('/api/articles/test',
                                              HTTP_AUTHORIZATION='Token ' + self.token,
                                              format='json')
        article = json.loads(response_article.content)

        self.assertIn(
            'Sorry, the article was not found', str(article))

        self.assertEqual(response_article.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_edit_article(self):
        """
        tests successfull edit for an article
        :return:
        """
        response0 = self.client.post('/api/articles/', self.article,
                                     HTTP_AUTHORIZATION='Token ' + self.token,
                                     format='json')
        result0 = json.loads(response0.content)
        slug = result0["article"]["slug"]
        response = self.client.put('/api/articles/' + slug, self.article0,
                                   HTTP_AUTHORIZATION='Token ' + self.token,
                                   format='json')
        result = json.loads(response.content)

        self.assertIn('Andela1', str(result))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorised_edit_article(self):
        """
        Tests if user2 can edit an article created by user1
        :return:
        """
        response0 = self.client.post('/api/articles/', self.article,
                                     HTTP_AUTHORIZATION='Token ' + self.token,
                                     format='json')
        result0 = json.loads(response0.content)
        slug = result0["article"]["slug"]
        response = self.client.put('/api/articles/' + slug, self.article0,
                                   HTTP_AUTHORIZATION='Token ' + self.token2,
                                   format='json')
        result = json.loads(response.content)

        self.assertIn('unauthorised to perform the action', str(result))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorised_delete_article(self):
        """
        Tests if user2 can delete an article created by user1
        :return:
        """
        response0 = self.client.post('/api/articles/', self.article,
                                     HTTP_AUTHORIZATION='Token ' + self.token,
                                     format='json')
        result0 = json.loads(response0.content)
        slug = result0["article"]["slug"]
        response = self.client.delete('/api/articles/' + slug, self.article0,
                                      HTTP_AUTHORIZATION='Token ' + self.token2,
                                      format='json')
        result = json.loads(response.content)

        self.assertIn('unauthorised to perform the action', str(result))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
