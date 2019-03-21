"""Test models"""
from django.db.utils import IntegrityError
from rest_framework.test import APITestCase

from ...authentication.models import User
from ...authentication.serializers import RegistrationSerializer
from ..models import UserProfile, NotifyMe
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

        self.user2 = {
            "email": "kibet@email.com",
            "username": "kibet",
            "password": "07921513542"
        }

        self.created_user = User.objects.create_user(**self.user)
        self.username_id = self.created_user.id

        self.profile = {
            "username_id": self.username_id,
            "bio": "am fantastic",
            "interests": "football",
            "favorite_quote": "Yes we can",
            "mailing_address": "P.O BOX 1080",
            "website": "http://www.web.com",
            "active_profile": True
        }

        self.article_notify = {
            "article_id": 3,
            "notification": "New article created" 
        }

        self.comment_notify = {
            "username_id": self.username_id,
            "notification": "Great article" 
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

        self.assertIn('violates', str(e.exception))

    def test_article_create_notification(self):
        """
        test create notification for new article
        """
        response = NotifyMe(**self.article_notify)
        response.save()

        self.assertEqual(response.notification, "New article created")

    def test_comment_create_notification(self):
        """
        test create notification for new comment
        """
        response = NotifyMe(**self.comment_notify)
        response.save()

        self.assertEqual(response.notification, "Great article")


