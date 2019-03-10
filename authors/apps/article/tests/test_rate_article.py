import json

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status


class TestRateArticle(APITestCase):
    """
    Class tests for rating article.
    """
    client = APIClient()

    def setUp(self):
        """ Creates user  and article for testing"""
        self.article = {
            "title": "epic",
            "description": "sdsd",
            "body": "dsd",
            "images": "",
            "tag_list":['kelvin','onkundi']
        }
        self.user = {
            "user": {
                "email": "winniekariuki07@gmail.com",
                "username": "Winnie",
                "password": "Winnie07"
            }
        }
        self.user_1 = {
            "user": {
                "email": "julietkariuki07@gmail.com",
                "username": "Juliet",
                "password": "Juliet07"
            }
        }
        
        self.rate = {
	        "your_rating":2
        }
        self.rate_update = {
	        "your_rating":3
        }
        self.rate_high = {
	        "your_rating":6
        }

        self.rate_low = {
	        "your_rating":0
        }

        create_user = self.client.post(
            '/api/users/', self.user, format='json')

        create_user_1 = self.client.post(
            '/api/users/', self.user_1, format='json')
            
        self.request_tkn = self.client.post(
            '/api/users/login/', self.user, format='json')
        token_request = json.loads(self.request_tkn.content)
        self.token = token_request["user"]["token"]

        self.request_tkn_1= self.client.post(
            '/api/users/login/', self.user_1, format='json')
        token_request_1 = json.loads(self.request_tkn_1.content)
        self.token_1 = token_request_1["user"]["token"]

        create_article = self.client.post('/api/articles/', self.article,
                                          HTTP_AUTHORIZATION='Token ' + self.token,
                                          format='json')

    def test_successful_rate(self):
        """Test rate article 
        
        """
        response = self.client.post('/api/rate/epic/', self.rate,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"], "rate_success")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rating_your_own_article(self):
        """
        Tests rating your own article
        """
        response = self.client.post('/api/rate/epic/', self.rate,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)


        self.assertEqual(result["errors"]["message"], "You cannot rate your own article")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_article_does_not_exist(self):
        """
        test rating an article that does not exist
        """
        response = self.client.post('/api/rate/kiwi/', self.rate,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)
       

        self.assertEqual(result["errors"]["message"], "The article does not exist")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
         
    def test_rate_above_five(self):
        """
        Test rate article above five 
        """
        response = self.client.post('/api/rate/epic/', self.rate_high,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["errors"]["your_rating"], ['You cannot rate above 5'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
          
    def test_rate_low_one(self):
        """
        Test rate article  low one
        """
        response = self.client.post('/api/rate/epic/', self.rate_low,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["errors"]["your_rating"], ['You cannot rate below 1'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rate_nulll(self):
        """
        Test rating an article without passing any value
        """
        response = self.client.post('/api/rate/epic/',
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["errors"]["your_rating"], ['rating is required'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_rate(self):
        """Test delete rate article 
        
        """
        response = self.client.post('/api/rate/epic/', self.rate,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        response = self.client.delete('/api/rate/epic/',
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result.get("message"), "Deleted successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_non_existent_rate(self):
        """Test delete rate article that does not exist
        
        """
        response = self.client.post('/api/rate/live/',
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        response = self.client.delete('/api/rate/live/',
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["errors"]["message"], 'Does not exist')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_get_rates(self):
        """Test get rates article 
        
        """
        response = self.client.post('/api/rate/epic/', self.rate,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        response = self.client.get('/api/rate/epic/',
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content) 

        self.assertEqual(result["message"], "successfull")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
 
    def test_get_rates_of_non_existing_article(self):
        """Test get rates article of non_existing article 
        
        """
        response = self.client.get('/api/rate/look/',
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content) 

        self.assertEqual(result["errors"]["message"], "No ratings for this article because the article does not exist")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_update_rate(self):
        """Test updating rate article 
        
        """
        response = self.client.post('/api/rate/epic/', self.rate,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)


        response = self.client.post('/api/rate/epic/', self.rate_update,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"], "rate_success")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
       
    def test_update_rate_article_not_existing(self):
        """Test updating rate article that does not exist
        
        """
        response = self.client.post('/api/rate/rock/', self.rate,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)


        response = self.client.post('/api/rate/rock/', self.rate_update,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)
        self.assertEqual(result["errors"]["message"], "The article does not exist")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            
       
   
   