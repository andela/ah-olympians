from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import UserProfile
from .renderers import ProfileJSONRenderer
from .serializers import (
    ProfileSerializer
)

class CreateProfileAPIView(CreateAPIView):
	""" A class that contains methods on creating user profile."""
	#permission_classes = (IsAuthenticated,)
	renderer_classes = (ProfileJSONRenderer,)
	queryset = UserProfile.objects.all()
	serializer_class = ProfileSerializer


	def perform_create(self, serializer):
		serializer.save(username=self.request.user)


class ViewUserProfileAPIView(ListAPIView):
	""" A class that contains methods on viewing user profiles."""
	#permission_classes = (IsAuthenticated,)
	renderer_classes = (ProfileJSONRenderer,)
	
	serializer_class = ProfileSerializer

	def get_queryset(self):
		""" Overrides queryset to get user profile with user_id
			specified in the URL)."""
		user_id = self.kwargs['user_id']
		return UserProfile.objects.filter(id=user_id)

