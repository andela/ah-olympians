from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
	bio = models.CharField(max_length=255, blank=True)
	avatar = CloudinaryField("image", default="image/upload/v1551960935/books.png")
	interests = models.CharField(max_length=255, blank=True)
	favorite_quote = models.CharField(max_length=100, blank=True)
	mailing_address = models.CharField(max_length=50, blank=True)
	website = models.URLField(blank=True, default='')
	contact_phone = models.IntegerField(blank=True, default=0)
	created = models.DateTimeField(auto_now_add=True)
	username = models.OneToOneField('authentication.User', related_name="profile", on_delete=models.CASCADE)
	following = models.BooleanField(default=False)
	active_profile = models.BooleanField(default=True)


	def __str__(self):
		return self.username


