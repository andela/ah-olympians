from django.urls import path

from .views import (
    CreateProfileAPIView, ViewUserProfileAPIView, EditUserProfileAPIView,
    ViewAllProfilesAPIView, DeactivateProfileAPIView, ActivateProfileAPIView,
    FollowAuthorAPIView, FollowingListAPIView, FollowerListAPIView
)

app_name = 'profiles'

urlpatterns = [
    path('create_profile/', CreateProfileAPIView.as_view()),
    path('edit_profile/', EditUserProfileAPIView.as_view()),
    path('view_profiles/', ViewAllProfilesAPIView.as_view()),
    path('view_profile/<username_id>', ViewUserProfileAPIView.as_view()),
    path('deactivate_profile/', DeactivateProfileAPIView.as_view()),
    path('activate_profile/', ActivateProfileAPIView.as_view()),
    path('view_profile/<username_id>/follow/', FollowAuthorAPIView.as_view()),
    path('view_profile/following/', FollowingListAPIView.as_view()),
    path('view_profile/followers/', FollowerListAPIView.as_view()),

    
]
