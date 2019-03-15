from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
	"""Serializes creation of user profile. """
	username = serializers.SlugRelatedField(read_only=True, slug_field='username')
	following = serializers.SerializerMethodField()

	def get_following(self, instance):
		request = self.context.get('request', None)

		if request is None:
			return None

		target_profile = request.user.profile
		status = target_profile.if_following(instance)

		return status

	class Meta:
		model = UserProfile
		extra_kwargs = {'active_profile': {'read_only': True}}
		fields = [
				'username', 'bio',
				'avatar', 'interests', 'favorite_quote',
				'website', 'following'
				]


class DeactivateSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = ['active_profile',]


class FollowSerializer(serializers.ModelSerializer):
	"""Serializes user following other users."""
	username = serializers.CharField(source='user.profile.username', read_only=True)
	following = serializers.SerializerMethodField()

	def get_following(self, instance):
		request = self.context.get('request', None)

		if request is None:
			return None

		target_profile = request.user.profile
		status = target_profile.if_following(instance)

		return status

	class Meta:
		model = UserProfile
		fields = ["following", "username"]


class FollowListSerializer(serializers.ModelSerializer):
	username = serializers.SlugRelatedField(read_only=True, slug_field='username')
	follow_since = serializers.ReadOnlyField(source="created_time")

	class Meta:
		model = UserProfile
		fields = ["username", "follow_since"]






