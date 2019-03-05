from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import UserProfile

class ProfileSerializer(serializers.ModelSerializer):
	"""Serializes creation of user profile. """
	username = serializers.SlugRelatedField(read_only=True, slug_field='username')

	class Meta:
		model = UserProfile
		extra_kwargs = {'active_profile': {'read_only': True}}
		fields = [
				'username_id', 'username', 'bio',
				'avatar', 'interests', 'favorite_quote',
				'created', 'mailing_address', 'website',
				'contact_phone', 'active_profile'
				]


class DeactivateSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = ['active_profile',]