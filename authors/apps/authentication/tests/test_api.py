

"""Test API endpoints"""

import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status

# tests for Endpoints


class UserTest(APITestCase):
    client = APIClient()

    def setUp(self):
        # add test data
        self.user = {
            "user": {
                "email": "caro@yahoo.com",
                "username": "caro",
                "password": "07921513542"
            }
        }

    def test_register_user(self):
        """
        test register
        """
        # hit the API endpoint
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)

        self.assertEqual(result["user"]["email"], "caro@yahoo.com")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_existing_email(self):
        """
        test register
        """
        # hit the API endpoint
        response = self.client.post('/api/users/', self.user, format='json')

        self.user['user']['username'] = "kimtai"
        self.user['user']['password'] = "4567890123"
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)

        self.assertIn('Email is already registered to another user', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user with this email already exists.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_register_user_empty_string(self):
        """
        test register
        """
        # hit the API endpoint
        response = self.client.post('/api/users/', self.user, format='json')

        self.user['user']['username'] = ""
        self.user['user']['password'] = ""
        response = self.client.post('/api/users/', self.user, format='json')
        result = json.loads(response.content)


        self.assertIn('A username is required to complete registration', str(result))
        self.assertIn('This field may not be blank.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_norequired(self):
        """
        test register without required fields
        """
        # hit the API endpoint
        response = self.client.post('/api/users/', format='json')
        result = json.loads(response.content)

        self.assertIn('errors', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        """
        test login
        """
        self.user['user']['email'] = "james@gmail.com"
        self.user['user']['password'] = "4567890123"
        # hit the API endpoint
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.assertIn(
            'A user with this email and password was not found.', str(result))
        response = self.client.post('/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.assertIn('A user with this email and password was not found.', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unregistered_user(self):
        """
        test login
        """
        # create user
        self.client.post('/api/users/', self.user, format='json')
        # hit the API endpoint
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        #create user
        self.client.post('/api/users/', self.user, format='json')
        # hit the API endpoint
        response = self.client.post('/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.assertIn('caro@yahoo.com', str(result))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_with_norequired(self):
        """
        test login user without required fields
        """

        # create user
        self.client.post('/api/users/', format='json')
        # hit the API endpoint
        response = self.client.post(
            '/api/users/login/', self.user, format='json')
        #create user
        self.client.post('/api/users/', format='json')
        # hit the API endpoint
        response = self.client.post('/api/users/login/', self.user, format='json')
        result = json.loads(response.content)

        self.assertIn('errors', str(result))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthenticated(self):
        """
        test retrieve user
        """

        #create user
        self.client.post('/api/users/', self.user, format='json')
        # hit the API endpoint
        response = self.client.get('/api/user/')
        result = json.loads(response.content)


        self.assertIn(
            'Authentication credentials were not provided.', str(result))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', str(result))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', str(result))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_update_user_unauthenticated(self):
        """
        test update user
        """
        self.user['user']['password'] = "4567890123"

        #create user
        self.client.post('/api/users/', self.user, format='json')
        # hit the API endpoint
        response = self.client.put('/api/user/', self.user, format='json')
        result = json.loads(response.content)


        self.assertIn(
            'Authentication credentials were not provided.', str(result))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', str(result))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Authentication credentials were not provided.', str(result))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
