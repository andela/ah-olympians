"""Test models"""

import json
from rest_framework.test import APITestCase, APIClient
from ..models import User
from ..serializers import RegistrationSerializer


# tests for Endpoints

class UserTest(APITestCase):
    client = APIClient()

    def setUp(self):
        # add test data
        self.user = {
            "email": "caro@email.com",
            "username": "caro",
            "password": "07921513542"

        self.user_model = User()
        self.user = {
                "email": "caro@email.com",
                "username": "caro",
                "password": "07921513542"

        }

        self.user_2 = User.objects.create_user("musa", "musa@email.com")

    def test_create_superuser(self):
        """
        test create superuser method
        """

        response = User.objects.create_superuser(
        response = User.objects.create_superuser(self.user["username"], self.user["email"], self.user["password"])
        response = User.objects.create_superuser(self.user["username"], self.user["email"], self.user["password"])
        serialized_user = RegistrationSerializer(response)

        self.assertEqual(serialized_user.data['email'], 'caro@email.com')

    def test_create_superuser_no_password(self):
        """
        test create user method
        """

        with self.assertRaises(TypeError) as error_message:
            User.objects.create_superuser(
                self.user["username"], self.user["email"], None)

        self.assertEqual(str(error_message.exception), 'Superusers must have a password.')
        with self.assertRaises(TypeError) as e:
            User.objects.create_superuser(self.user["username"], self.user["email"], None)

        self.assertEqual(str(e.exception), 'Superusers must have a password.')

    def test_create_user_no_username(self):
        """
        test create user method
        """
        with self.assertRaises(TypeError) as error_message:
            User.objects.create_user(None, self.user["email"])

        self.assertEqual(str(error_message.exception), 'Users must have a username.')

        with self.assertRaises(TypeError) as e:
            User.objects.create_user(None, self.user["email"])

        self.assertEqual(str(e.exception), 'Users must have a username.')

    def test_create_user_no_email(self):
        """
        test create user method
        """

        with self.assertRaises(TypeError) as error_message:
            User.objects.create_user(self.user["username"], None)

        self.assertEqual(str(error_message.exception), 'Users must have an email address.')
        with self.assertRaises(TypeError) as e:
            User.objects.create_user(self.user["username"], None)

        self.assertEqual(str(e.exception), 'Users must have an email address.')


    def test_user_representation(self):
        """Test if proper string representation is returned"""
        self.assertEqual(str(self.user_2), "musa@email.com")

    def test_user_get_short_name(self):
        """Test method to get short name"""
        self.assertEqual(self.user_2.get_short_name(), "musa")

    def test_user_get_full_name(self):
        """Test method to get full user name"""

        self.assertEqual(self.user_2.get_full_name(), "musa")
        self.assertEqual(self.user_2.get_full_name, "musa")

