import json

from rest_framework.test import APITestCase,APIClient
from rest_framework.views import status

class TestCreateArticleWithTag(APITestCase):
    '''
    base class for tests 
    '''

    client = APIClient()

    def setUp(self):
        """
        Create dummy data for testing
        """

        self.article = {
            "title":"we love Andela",
            "description":"i love Andela",
            "body":"andela is a cool place",
            "images":"",
            "tag_list":["andela","kenya"]
        }

        self.article1 = {
            "title":"we love Andela",
            "description":"i love Andela",
            "body":"andela is a cool place",
            "images":"",
            "tag_list":"andela"
        }

        self.user = {
            "user": {
                "email": "chirchir@olympians.com",
                "username": "chirchir",
                "password": "test1234"
            }
        }

        self.article3 = {
            "title":"we love Andela",
            "description":"i love Andela",
            "body":"andela is a cool place",
            "images":"",
            "tag_list":[1,23]
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


    def test_create_article(self):
        """Tests a request which belongs to a valid json file for article
        :return:
        """
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_article_invalid_tag_list(self):
        """Tests a request which belongs to a valid json file for article
        :return:
        """
        response = self.client.post('/api/articles/', self.article1,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_article_with_invalid_tag(self):
        '''
        create an article with empty tag field
        '''

        response = self.client.post('/api/articles/', self.article3,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
