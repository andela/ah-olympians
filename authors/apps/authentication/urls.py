from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    UserEmailVerification, ResetPasswordRequestAPIView,
    SetNewPasswordAPIView
)

app_name = 'authentication'

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('users/verify/', UserEmailVerification.as_view()),
    path('users/reset_password/', ResetPasswordRequestAPIView.as_view()),
    path('users/reset_password/<reset_token>', SetNewPasswordAPIView.as_view())
]
