"""Test models"""
from django.db.utils import IntegrityError
from rest_framework.test import APITestCase

from ...authentication.models import User
from ...authentication.serializers import RegistrationSerializer
from ..models import UserProfile
from ..serializers import (
    ProfileSerializer, DeactivateSerializer)


class ModelsTest(APITestCase):
    """ Class contains method on testing profile creation."""

    def setUp(self):
        # add test data
        self.user = {
            "email": "caro@email.com",
            "username": "caro",
            "password": "07921513542"
        }

        self.created_user = User.objects.create_user(**self.user)
        username_id = self.created_user.id

        self.profile = {
            "username_id": username_id,
            "bio": "am fantastic",
            "interests": "football",
            "favorite_quote": "Yes we can",
            "mailing_address": "P.O BOX 1080",
            "website": "http://www.web.com",
            "active_profile": True
        }


    def test_create_profile(self):
        """
        test create profile method
        """
        response = UserProfile(**self.profile)
        response.save()


        self.assertEqual(response.bio, 'am fantastic')

    def test_create_same_profile(self):
        """
        test create profile twice
        """
        res= UserProfile(**self.profile)
        res.save()

        # Create same profile
        res2 = UserProfile(**self.profile)

        with self.assertRaises(IntegrityError) as e:
            res2.save()

        self.assertIn('duplicate key', str(e.exception))
