from rest_framework import status
from rest_framework.exceptions import APIException


def validate_avatar(avatar_name):
	""" Validates whether avatar is an image."""
	if avatar_name == None:
		return True

	ok_formats = [
					".png",
					".jpg",
					".jpeg"
				]
				
	avatar_name =str(avatar_name)

	if not avatar_name.lower().endswith((*ok_formats,)):
		APIException.status_code = status.HTTP_400_BAD_REQUEST
		raise APIException({"message":
			"Only '{}', '{}', '{}' files are accepted".format(*ok_formats)})