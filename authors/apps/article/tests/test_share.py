import json

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.urls import reverse
import pdb


class TestShareArticle(APITestCase):
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
        
    def get_share_link(self, slug, provider):
        return self.client.get(
        reverse(
                "share_article",
                kwargs={
                    "slug": slug,
                    "provider": provider
                }),
            HTTP_AUTHORIZATION="Token {}".format(self.token)
        )
    def successful_article(self):
        """Tests a request which belongs to a valid json file for article
        :return:
        """
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)
        return result

    
    def get_article_slug(self):
        """
        return a slug appended to an article
        """
        return self.successful_article()['article']['slug']

    def test_facebook_correct_share(self):

        article_slug = self.get_article_slug()
        res = self.client.get(
            '/api/articles/{}/share/facebook'.format(article_slug),HTTP_AUTHORIZATION='Token ' + self.token)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_twitter_correct_share(self):

        article_slug = self.get_article_slug()
        res = self.client.get(
            '/api/articles/{}/share/twitter'.format(article_slug),HTTP_AUTHORIZATION='Token ' + self.token)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reddit_correct_share(self):

        article_slug = self.get_article_slug()
        res = self.client.get(
            '/api/articles/{}/share/reddit'.format(article_slug),HTTP_AUTHORIZATION='Token ' + self.token)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_linkedin_correct_share(self):

        article_slug = self.get_article_slug()
        res = self.client.get(
            '/api/articles/{}/share/linked'.format(article_slug),HTTP_AUTHORIZATION='Token ' + self.token)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_email_correct_share(self):

        article_slug = self.get_article_slug()
        res = self.client.get(
            '/api/articles/{}/share/linked'.format(article_slug),HTTP_AUTHORIZATION='Token ' + self.token)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
