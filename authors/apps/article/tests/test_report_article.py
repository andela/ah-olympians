import json

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status


class TestReportArticle(APITestCase):
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
            "images": ""
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
        self.admin = {
            "user": {
                "email": "andelaolympians@andela.com",
                "username": "andela",
                "password": "Kariuki07"
            }
        }
        
        self.report = {
	       "report_message":"plagerism"
        }
      

        create_user = self.client.post(
            '/api/users/', self.user, format='json')

        create_user_1 = self.client.post(
            '/api/users/', self.user_1, format='json')
        create_admin = self.client.post(
            '/api/users/', self.admin, format='json')
        
            
        self.request_tkn = self.client.post(
            '/api/users/login/', self.user, format='json')
        token_request = json.loads(self.request_tkn.content)
        self.token = token_request["user"]["token"]

        self.request_tkn_1= self.client.post(
            '/api/users/login/', self.user_1, format='json')
        token_request_1 = json.loads(self.request_tkn_1.content)
        self.token_1 = token_request_1["user"]["token"]

        self.request_tkn_admin= self.client.post(
            '/api/users/login/', self.admin, format='json')
        token_request_admin= json.loads(self.request_tkn_admin.content)
        self.token_admin = token_request_admin["user"]["token"]

        create_article = self.client.post('/api/articles/', self.article,
                                          HTTP_AUTHORIZATION='Token ' + self.token,
                                          format='json')
    def test_successful_report(self):
        """Test reporting of an article 
        
        """
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.post('/api/report/epic/', self.report,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"], "Your report has been sent successfully to the admin ")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_report_of_article_does_not_exist(self):
        """Test reporting of an article that does not exist
        
        """
        from rest_framework.test import APIClient
        client = APIClient()
        response = client.post('/api/report/spoon/', self.report,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["error_message"], "The article you are reporting does not exist")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_reporting_your_own_article(self):
        """Test reporting your own article
        
        """
    
        response = self.client.post('/api/articles/', self.article,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)
        
        response = self.client.post('/api/report/epic/', self.report,
                                    HTTP_AUTHORIZATION='Token ' + self.token,
                                    format='json')
        result = json.loads(response.content)
        
        self.assertEqual(result["errors"], "You cannot report your own article")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_report_article_more_than_once(self):
        """Test reporting of an article 
        
        """
        from rest_framework.test import APIClient
        client = APIClient()

        response = client.post('/api/report/epic/', self.report,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        response = client.post('/api/report/epic/', self.report,
                                    HTTP_AUTHORIZATION='Token ' + self.token_1,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result['errors'],'You can only report an article once')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_all_reports(self):
        """
        Test getting of all reports
        
        """ 
        from rest_framework.test import APIClient
        client = APIClient()
         
        response = self.client.get('/api/reports/',
                                    HTTP_AUTHORIZATION='Token ' + self.token_admin,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"], "You have no permissions")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_get_single_report(self):
        """
        Test getting of single report
        
        """ 
        from rest_framework.test import APIClient
        client = APIClient()
         
        response = self.client.get('/api/reports/epic/',
                                    HTTP_AUTHORIZATION='Token ' + self.token_admin,
                                    format='json')
        result = json.loads(response.content)

        self.assertEqual(result["message"], "You have no permissions")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
