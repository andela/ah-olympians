from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status, response
from rest_framework.generics import (
	CreateAPIView, ListAPIView, RetrieveUpdateAPIView,
	RetrieveAPIView, ListCreateAPIView
	)
from rest_framework.permissions import (
	IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

import psycopg2

from .models import UserProfile
from .renderers import (
	ProfileJSONRenderer, FollowListJSONRenderer)
from .serializers import (
    ProfileSerializer, DeactivateSerializer, 
    FollowSerializer, FollowListSerializer
)
from .custom_validations import validate_avatar


class CreateProfileAPIView(CreateAPIView):
	""" A class that contains methods on creating user profile."""

	permission_classes = (IsAuthenticated,)
	renderer_classes = (ProfileJSONRenderer,)
	queryset = UserProfile.objects.all()
	serializer_class = ProfileSerializer

	def perform_create(self, serializer):
		""" Overrides create method to allow for validation."""
		avatar_name = self.request.data.get("avatar")
		validate_avatar(avatar_name)

		try:
			get_object_or_404(self.get_queryset(), username_id=self.request.user.id, active_profile=False)
		except Http404:
			pass
		else:
			raise APIException({"message":
				"You deactivated your profile. Please activate to continue"})

		try:
			serializer.save(username=self.request.user)
		except (psycopg2.IntegrityError, IntegrityError):
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException(
					{"message": "A user with this profile already exists"})





class EditUserProfileAPIView(RetrieveUpdateAPIView):
	""" A class that contains methods on updating user profiles."""

	lookup_field = "username_id"
	permission_classes = (IsAuthenticated,)
	renderer_classes = (ProfileJSONRenderer,)
	serializer_class = ProfileSerializer
	queryset = UserProfile.objects.all()


	def get_object(self):
		""" Overrides queryset to get a single object."""
		if self.request.data.get("avatar"):
			validate_avatar(self.request.data.get("avatar"))

		serializer = ProfileSerializer(partial=True)
		queryset = self.filter_queryset(self.get_queryset())

		try:
			my_profile = queryset.get(username_id=self.request.user.id)
		except UserProfile.DoesNotExist:
			APIException.status_code = status.HTTP_404_NOT_FOUND
			raise APIException ({
				"message": "User profile not found. Please create one"
				})
		return my_profile


class ViewUserProfileAPIView(RetrieveAPIView):
	""" A class that contains methods on viewing a user profile."""

	lookup_field = "username_id"
	permission_classes = (IsAuthenticatedOrReadOnly,)
	renderer_classes = (ProfileJSONRenderer,)
	serializer_class = ProfileSerializer

	def get_queryset(self):
		""" Overrides queryset to get user profile with user_id
			specified in the URL)."""
		try:
			username_id = self.kwargs['username_id']
			int(username_id)
		except ValueError:
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException ({"message": "User ID must be an integer"})

		try:
			UserProfile.objects.get(username_id=username_id, active_profile=True)
		except (Exception, UserProfile.DoesNotExist):
			APIException.status_code = status.HTTP_404_NOT_FOUND
			raise APIException ({"message": "User profile does not exist"})

		return UserProfile.objects.filter(username_id=username_id)


class ViewAllProfilesAPIView(ListAPIView):
	""" A class that contains methods on viewing all user profiles."""

	permission_classes = (IsAuthenticated,)
	renderer_classes = (ProfileJSONRenderer,)
	serializer_class = ProfileSerializer
	queryset = UserProfile.objects.all()

	def list(self, request):
		""" Overrides list to check if there are registered profiles."""
		try:
			try:
				UserProfile.objects.get(active_profile=True)
			except UserProfile.MultipleObjectsReturned:
				pass
		except UserProfile.DoesNotExist:
			APIException.status_code = status.HTTP_404_NOT_FOUND
			raise APIException ({"message": "No user profiles found"})

		queryset = self.queryset.filter(active_profile=True)
		serializer = self.get_serializer(queryset, many=True)
		data = {obj['username']: obj for obj in serializer.data}
		return Response({'profiles': data})



class DeactivateProfileAPIView(RetrieveUpdateAPIView):
	""" A class that contains methods of deactivating a profile."""

	lookup_field = "username_id"
	permission_classes = (IsAuthenticated,)
	renderer_classes = (ProfileJSONRenderer,)
	serializer_class = DeactivateSerializer
	queryset = UserProfile.objects.all()

	def get_object(self):
		""" Retrieves active user's profile."""
		serializer = self.serializer_class
		queryset = self.filter_queryset(self.get_queryset())

		try:
			my_profile = queryset.get(username_id=self.request.user.id)
		except (Exception, UserProfile.DoesNotExist):
			APIException.status_code = status.HTTP_404_NOT_FOUND
			raise APIException ({"message": "User profile not found"})

		try:
			get_object_or_404(self.get_queryset(), username_id=self.request.user.id, active_profile=False)
		except Http404:
			pass
		else:
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException({"message":
				"You deactivated your profile. Please activate to continue"})

		return my_profile

	def update(self, request):
		""" Set's profile status to not active."""
		data = {"active_profile": "False"}
		profile = self.get_object()
		serializer = DeactivateSerializer(profile, data=data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateProfileAPIView(RetrieveUpdateAPIView):
	""" A class that contains methods of deactivating a profile."""

	lookup_field = "username_id"
	permission_classes = (IsAuthenticated,)
	renderer_classes = (ProfileJSONRenderer,)
	serializer_class = DeactivateSerializer
	queryset = UserProfile.objects.all()

	def get_object(self):
		""" Retrieves active user's profile."""
		serializer = self.serializer_class
		queryset = self.filter_queryset(self.get_queryset())


		try:
			my_profile = queryset.get(username_id=self.request.user.id)
		except (Exception, UserProfile.DoesNotExist):
			APIException.status_code = status.HTTP_404_NOT_FOUND
			raise APIException ({"message": "User profile not found"})

		try:
			get_object_or_404(self.get_queryset(),
				username_id=self.request.user.id, active_profile=True)
		except Http404:
			pass
		else:
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException({"message":
				"Your profile is already active and viewable by other users"})

		return my_profile

	def update(self, request):
		""" Set's profile status to not active."""
		data = {"active_profile": "True"}
		profile = self.get_object()
		serializer = DeactivateSerializer(profile, data=data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowAuthorAPIView(APIView):
	""" A class that contains methods for following other users."""

	serializer_class = FollowSerializer
	permission_classes = (IsAuthenticated,)
	queryset = UserProfile.objects.all()


	def get_username_id(self):
		""" A method for validating username_id."""
		try:
			username_id = int(self.kwargs.get("username_id"))
		except ValueError:
			raise APIException({"message": "User ID must be an integer"})
		try:
			self.queryset.get(username_id=username_id)
		except UserProfile.DoesNotExist:
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException({"message":
				"We did not find such a profile."})
		return username_id

	def post(self, request, *args, **kwargs):
		""" A method for following other users."""
		username_id = self.get_username_id()
		my_profile = self.request.user.profile
		target_profile = UserProfile.objects.get(username_id=username_id)

		if my_profile.username_id == username_id:
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException({"message":
				"You cannot follow yourself."})

		if my_profile.following.filter(username_id=username_id):
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException({"message":
				"{}, you already follow {}".format(my_profile.username.username, 
					target_profile.username.username)})


		my_profile.follow(target_profile)
		serializer = self.serializer_class(target_profile, context={'request': self.request})

		if serializer.data["following"]:
			return Response(
				{"message":
				"{}, you have successfully followed {}".format(my_profile.username.username, 
					target_profile.username.username)})

	def delete(self, request, *args, **kwargs):
		""" A method for unfollowing followed users."""
		username_id = self.get_username_id()
		my_profile = self.request.user.profile
		target_profile = UserProfile.objects.get(username_id=username_id)

		if my_profile.username_id == username_id:
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException({"message":
				"You cannot unfollow yourself."})

		if not my_profile.following.filter(username_id=username_id):
			APIException.status_code = status.HTTP_400_BAD_REQUEST
			raise APIException({"message":
				"{}, you do not follow {}".format(my_profile.username.username, 
					target_profile.username.username)})

		my_profile.unfollow(target_profile)
		serializer = self.serializer_class(target_profile, context={'request': self.request})

		if not serializer.data["following"]:
			return Response(
				{"message":
				"{}, you have successfully unfollowed {}".format(my_profile.username.username, 
					target_profile.username.username)})


class FollowerListAPIView(ListAPIView):
	""" A class that contains methods on getting list of users a user follows."""

	permission_classes = (IsAuthenticated,)
	renderer_classes = (FollowListJSONRenderer,)
	serializer_class = FollowListSerializer
	queryset = UserProfile.objects.all()


	def list(self, request, *args, **kwargs):
		""" A method that overrides list to get user-specific data."""
		queryset = request.user.profile.followed_by.all()
		serializer = self.serializer_class(queryset, many=True)
		data = {obj['username']: obj for obj in serializer.data}
		return Response({"followers": data})

class FollowingListAPIView(ListAPIView):
	""" A class that contains methods on getting list of users that follow a user."""

	permission_classes = (IsAuthenticated,)
	renderer_classes = (FollowListJSONRenderer,)
	serializer_class = FollowListSerializer
	queryset = UserProfile.objects.all()


	def list(self, request, *args, **kwargs):
		""" A method that overrides list to get user-specific data."""
		queryset = request.user.profile.following.all()
		serializer = self.serializer_class(queryset, many=True)
		data = {obj['username']: obj for obj in serializer.data}
		return Response({"following": data})





		



