import json

from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status


class TestSearch(APITestCase):
    """ This class tests the Article Search and Filtering feature
    """

    client = APIClient()

    def setUp(self):
        """ This is the set-up method for all feature tests
        """

        self.user = {
            "user": {
                "username": "kibet",
                "email": "kibet@olympians.com",
                "password": "qwerty12"
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

        self.article1 = {
            "title": "Andela",
            "description": "be epic",
            "body": "powering todays teams",
            "images": ""
        }
        self.article2 = {
            "title": "Learning some vim",
            "description": "Vim is awesome",
            "body": "Just random text to test search",
            "images": "",
            "tag_list": ['programming', 'code']
        }

        # create user
        self.client.post('/api/users/', self.user, format='json')

        response = self.client.post(
            '/api/users/login/', self.user, format='json')

        result = json.loads(response.content)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + result["user"]["token"])

        profile = self.client.post(
            '/api/profile/create_profile/', self.profile, format='json')
        prof_result = json.loads(profile.content)

        article = self.client.post(
            '/api/articles/', self.article1, format='json')

        article = self.client.post(
            '/api/articles/', self.article2, format='json')

    def test_empty_search(self):
        """ Test search when no query params are provided
        """
        response = self.client.get('/api/search/articles', format='json')
        result = json.loads(response.content)

        self.assertIn('Please provide a search phrase', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_not_found(self):
        """ Test search for non-existing article
        """
        response = self.client.get(
            '/api/search/articles?search=going&home',
            format='json')
        result = json.loads(response.content)

        self.assertIn('Sorry we could not find what you are looking for.',
                      str(result))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_found(self):
        """ Test search found and article
        """
        response = self.client.get(
            '/api/search/articles?search=learn&vim',
            format='json')
        result = json.loads(response.content)

        self.assertIn('Just random text to test search', str(result))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_on_article_author(self):
        """ Test article search with title and author
        """
        response = self.client.get(
            '/api/search/articles?search=learn&vim&author=kibet',
            format='json')
        result = json.loads(response.content)

        self.assertIn('Just random text to test search', str(result))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_author(self):
        """ Test article search with title and author
        """
        response = self.client.get(
            '/api/search/articles?author=kibet',
            format='json')
        result = json.loads(response.content)

        self.assertIn('Just random text to test search', str(result))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_with_tag(self):
        """ Test article search with title and author
        """
        response = self.client.get(
            '/api/search/articles?tag=code',
            format='json')
        result = json.loads(response.content)

        self.assertIn('Just random text to test search', str(result))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mismatch_tag_title(self):
        """ Test article search with title and author
        """
        response = self.client.get(
            '/api/search/articles?title=andela&tag=code',
            format='json')
        result = json.loads(response.content)

        self.assertIn('Sorry we could not find what you are looking for.',
                      str(result))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
