from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import UserProfile, NotifyMe


class ProfileSerializer(serializers.ModelSerializer):
	"""Serializes creation of user profile. """
	username = serializers.SlugRelatedField(read_only=True, slug_field='username')
	following = serializers.SerializerMethodField()

	def get_following(self, instance):
		"""Serializer method field that checks if following."""
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
				'website', 'following', 'username_id'
				]


class DeactivateSerializer(serializers.ModelSerializer):
	"""Serializes user deactivating their profile. """
	class Meta:
		model = UserProfile
		fields = ['active_profile',]


class FollowSerializer(serializers.ModelSerializer):
	"""Serializes user following other users."""
	username = serializers.CharField(source='user.profile.username', read_only=True)
	following = serializers.SerializerMethodField()

	def get_following(self, instance):
		"""Serializer method field that checks if following."""
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

class NotificationSerializer(serializers.ModelSerializer):
	"""Serializes creation of notifications."""
	username = serializers.SlugRelatedField(read_only=True, slug_field='email')

	class Meta:
		model = NotifyMe
		fields = ["username",]

class NotifySerializer(serializers.ModelSerializer):
	"""Serializes notifications list and includes a time since the item was posted."""
	username = serializers.SlugRelatedField(read_only=True, slug_field='username')
	time_posted = serializers.ReadOnlyField(source="created_time")

	class Meta:
		model = NotifyMe
		fields = ["username", "notification", "time_posted", "slug", ]


class OptNotificationSerializer(serializers.ModelSerializer):
	"""Serializes user enabling/disabling notifications. """
	class Meta:
		model = UserProfile
		fields = ['in_app_notify',]


class EmailNotificationSerializer(serializers.ModelSerializer):
	"""Serializes user enabling/disabling email notifications. """
	class Meta:
		model = UserProfile
		fields = ['email_notify',]

