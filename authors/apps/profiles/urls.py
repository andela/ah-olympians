from django.urls import path

from .views import (
    CreateProfileAPIView, ViewUserProfileAPIView
)

app_name = 'profiles'

urlpatterns = [
    path('create_profile/', CreateProfileAPIView.as_view()),
    path('create_profile/<user_id>', ViewUserProfileAPIView.as_view()),
]
