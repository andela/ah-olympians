from rest_framework.test import APITestCase
from rest_framework.exceptions import APIException

from ..custom_validations import validate_avatar as vd


class ValidationTest(APITestCase):
	""" Class to test custom validations."""

	def setUp (self):
		"""
		Sample avatars
		"""
		self.avatar_1 = "test.pdf"
		self.avatar_2 = "test.docx"
		self.avatar_3 = "test.py"
		self.avatar_4 = None

	def test_pdf_avatar(self):
		"""
		If user uploads .pdf
		"""
		with self.assertRaises(APIException) as e:
			vd(self.avatar_1)

		self.assertIn('files are accepted', str(e.exception))

	def test_doc_avatar(self):
		"""
		If user uploads .docx
		"""
		with self.assertRaises(APIException) as e:
			vd(self.avatar_2)

		self.assertIn('files are accepted', str(e.exception))

	def test_py_avatar(self):
		"""
		If user uploads .py
		"""
		with self.assertRaises(APIException) as e:
			vd(self.avatar_3)

		self.assertIn('files are accepted', str(e.exception))

	def test_no_avatar(self):
		"""
		If user does not provide avatar
		"""
		response = vd(self.avatar_4)

		self.assertEqual(response, True)

