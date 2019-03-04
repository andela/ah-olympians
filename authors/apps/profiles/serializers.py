from rest_framework import serializers

from .models import UserProfile

class ProfileSerializer(serializers.ModelSerializer):
	"""Serializes creation of user profile. """
	username = serializers.SlugRelatedField(read_only=True, slug_field='username')

	class Meta:
		model = UserProfile
		fields = ['username', 'bio', 'avatar', 'interests', 'favorite_quote', 'created', 'mailing_address']