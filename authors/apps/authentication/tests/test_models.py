<<<<<<< HEAD
<<<<<<< HEAD
"""Test models"""
=======
import json
>>>>>>> chore(write test for endpoints): writes tests for api endpoints
=======
import json
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints
from rest_framework.test import APITestCase, APIClient
from ..models import User
from ..serializers import RegistrationSerializer

<<<<<<< HEAD
<<<<<<< HEAD
=======
# tests for Endpoints

>>>>>>> chore(write test for endpoints): writes tests for api endpoints
=======
# tests for Endpoints

>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints

class UserTest(APITestCase):
    client = APIClient()

    def setUp(self):
        # add test data
<<<<<<< HEAD
<<<<<<< HEAD
        self.user = {
            "email": "caro@email.com",
            "username": "caro",
            "password": "07921513542"
=======
=======
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints
        self.user_model = User()
        self.user = {
                "email": "caro@email.com",
                "username": "caro",
                "password": "07921513542"
<<<<<<< HEAD
>>>>>>> chore(write test for endpoints): writes tests for api endpoints
=======
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints
        }

        self.user_2 = User.objects.create_user("musa", "musa@email.com")

    def test_create_superuser(self):
        """
        test create superuser method
        """
<<<<<<< HEAD
<<<<<<< HEAD
        response = User.objects.create_superuser(
            self.user["username"], self.user["email"], self.user["password"])
=======
        response = User.objects.create_superuser(self.user["username"], self.user["email"], self.user["password"])
>>>>>>> chore(write test for endpoints): writes tests for api endpoints
=======
        response = User.objects.create_superuser(self.user["username"], self.user["email"], self.user["password"])
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints
        serialized_user = RegistrationSerializer(response)

        self.assertEqual(serialized_user.data['email'], 'caro@email.com')

    def test_create_superuser_no_password(self):
        """
        test create user method
        """
<<<<<<< HEAD
<<<<<<< HEAD
        with self.assertRaises(TypeError) as error_message:
            User.objects.create_superuser(
                self.user["username"], self.user["email"], None)

        self.assertEqual(str(error_message.exception), 'Superusers must have a password.')
=======
=======
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints
        with self.assertRaises(TypeError) as e:
            User.objects.create_superuser(self.user["username"], self.user["email"], None)

        self.assertEqual(str(e.exception), 'Superusers must have a password.')
<<<<<<< HEAD
>>>>>>> chore(write test for endpoints): writes tests for api endpoints
=======
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints

    def test_create_user_no_username(self):
        """
        test create user method
        """
<<<<<<< HEAD
<<<<<<< HEAD
        with self.assertRaises(TypeError) as error_message:
            User.objects.create_user(None, self.user["email"])

        self.assertEqual(str(error_message.exception), 'Users must have a username.')
=======
=======
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(None, self.user["email"])

        self.assertEqual(str(e.exception), 'Users must have a username.')
<<<<<<< HEAD
>>>>>>> chore(write test for endpoints): writes tests for api endpoints
=======
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints

    def test_create_user_no_email(self):
        """
        test create user method
        """
<<<<<<< HEAD
<<<<<<< HEAD
        with self.assertRaises(TypeError) as error_message:
            User.objects.create_user(self.user["username"], None)

        self.assertEqual(str(error_message.exception), 'Users must have an email address.')
=======
=======
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(self.user["username"], None)

        self.assertEqual(str(e.exception), 'Users must have an email address.')
<<<<<<< HEAD
>>>>>>> chore(write test for endpoints): writes tests for api endpoints
=======
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints

    def test_user_representation(self):
        """Test if proper string representation is returned"""
        self.assertEqual(str(self.user_2), "musa@email.com")

    def test_user_get_short_name(self):
        """Test method to get short name"""
        self.assertEqual(self.user_2.get_short_name(), "musa")

    def test_user_get_full_name(self):
        """Test method to get full user name"""
<<<<<<< HEAD
<<<<<<< HEAD
        self.assertEqual(self.user_2.get_full_name(), "musa")
=======
        self.assertEqual(self.user_2.get_full_name, "musa")
        
        
>>>>>>> chore(write test for endpoints): writes tests for api endpoints
=======
        self.assertEqual(self.user_2.get_full_name, "musa")
        
        
>>>>>>> e2038e7... chore(write test for endpoints): writes tests for api endpoints
