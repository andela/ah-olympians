from django.conf import settings
from django.db import models
from django.utils.timesince import timesince

from cloudinary.models import CloudinaryField


class UserProfile(models.Model):
	bio = models.CharField(max_length=255, blank=True)
	avatar = CloudinaryField("image", default="image/upload/v1551960935/books.png")
	interests = models.CharField(max_length=255, blank=True)
	favorite_quote = models.CharField(max_length=100, blank=True)
	mailing_address = models.CharField(max_length=50, blank=True)
	website = models.URLField(blank=True, default='')
	contact_phone = models.IntegerField(blank=True, default=0)
	created = models.DateTimeField(auto_now_add=True)
	username = models.OneToOneField('authentication.User', related_name="profile", on_delete=models.CASCADE, primary_key=True)
	following = models.ManyToManyField('self', symmetrical=False, related_name="followed_by")
	active_profile = models.BooleanField(default=True)

	def follow(self, user2):
		self.following.add(user2)

	def unfollow(self, user2):
		self.following.remove(user2)

	def if_following(self, user2):
		return self.following.filter(pk=user2.username_id).exists()

	def following_list(self, username_id=None):
		my_follows = self.following.all()
		return my_follows

	def created_time(self):
	   return timesince(self.created)

	def __str__(self):
	    return self.username
