import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
import uuid
import unittest

from ..utils import send_email, verify_message
from ..models import User


class TestEmailIntergration(unittest.TestCase):
    """
    This class tests sending email with sendgrid and
    """
    def test_success_email(self):
        self.assertEqual(send_email("test@test.com", "test", "test"), 'email sent')

    def test_failed_email(self):
        """
        Testing providing a string instead of email
        """
        self.assertEqual(send_email("testtestcom", "test", "test"), 'There was an error sending')


class TestVerificationMessage(unittest.TestCase):
    """
    This class tests sending email with sendgrid and
    """
    def test_name_message(self):
        self.assertIn("Chirchir", verify_message("Chirchir", "token"))

    def test_token_message(self):
        token = str(uuid.uuid4())
        self.assertIn(token, verify_message("Chirchir", token))

