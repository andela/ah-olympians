from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
	bio = models.CharField(max_length=255)
	avatar = CloudinaryField('image')
	interests = models.CharField(max_length=50)
	favorite_quote = models.CharField(max_length=20)
	mailing_address = models.CharField(max_length=50)
	created = models.DateTimeField(auto_now_add=True)
	username = models.CharField(max_length=36)
	# username = models.ForeignKey('authentication.User', on_delete=models.CASCADE)


	def __str__(self):
		return self.username

