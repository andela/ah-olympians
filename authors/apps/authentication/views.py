from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from social_core.exceptions import MissingBackend
from social_django.utils import load_strategy, load_backend
from social_core.backends.oauth import BaseOAuth2, BaseOAuth1
from .backends import JWTAuthentication
from .models import User, EmailVerification
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    PasswordResetRequestSerializer, SetNewPasswordSerializer,
    EmailVerificationSerializer, SocialSerializer)

from .models import EmailVerification
from .renderers import UserJSONRenderer
from .utils import send_email, verify_message


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        new_user_data = request.data.get('user', {})
        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=new_user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = user.create_token()
        user_email = user.email
        username = user.username
        sign_up_message = verify_message(username, token)
        send_email(user_email, "Verify Your Email to Complete Your Authors Haven Registration", sign_up_message)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialAuthentication(CreateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialSerializer

    def create(self, request, *args, **kwargs):
        '''
        Fetch the access token and then create a user or
        authenticate a user
        '''

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        authenticated_user = request.user if not request.user.is_anonymous else None
        provider = serializer.data['provider']

        strategy = load_strategy(request)
        try:
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend as error:
            return Response(
                {
                    "errors": {
                        "provider": ["provider was not found", str(error)]
                    }
                }, status=status.HTTP_404_NOT_FOUND)

        if isinstance(backend, BaseOAuth1):
            token = {
                "oauth_token": serializer.data.get('access_token'),
                "oauth_token_secret": serializer.data.get('access_token_secret')
            }

        if isinstance(backend, BaseOAuth2):
            # Fetch the access token
            token = serializer.data['access_token']
        try:
            # check if there is an authenticated user,if true create a new one
            user = backend.do_auth(token, user=authenticated_user)
            print(user)
        except BaseException as error:
            # you cannot associate a social account with more than one user

            return Response({"errors": str(error)}, status=status.HTTP_400_BAD_REQUEST
                            )

        if user and user.is_active:
            serializer = UserSerializer(user)

            serializer.instance = user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': "Social aunthentication error"},
                            status=status.HTTP_400_BAD_REQUEST)


class UserEmailVerification(APIView):
    renderer_classes = (UserJSONRenderer,)
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.data['token']
        try:
            verification = EmailVerification.objects.get(token=token)
            if not verification.is_valid:
                return Response({"error": "Token already used"}, status=status.HTTP_400_BAD_REQUEST)
            verification.is_valid = False
            verification.save()
            return Response({"success": "valid token"}, status=status.HTTP_200_OK)
        except EmailVerification.DoesNotExist:
            return Response({"error": "invalid token"}, status=status.HTTP_403_FORBIDDEN)


class ResetPasswordRequestAPIView(APIView):
    """This view class provides a view to request a password reset.
    :return: http Response object
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        """This method gives a POST API view to request for password reset
        :param request: http request object
        :return: http Response
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        send = User.send_reset_token(serializer, request)
        return Response({'message': send}, status=status.HTTP_202_ACCEPTED)


class SetNewPasswordAPIView(APIView):
    """
    This view class provides a view to update and hence reset password
    :return: http Response
    """
    permission_classes = (AllowAny,)

    def put(self, request, reset_token):
        """This method gives a PUT API view to set new password
        :param request: http request object
        :param reset_token: password reset token sent to user
        :return: http response message
        """
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = request.data['password']
            user_credentials = JWTAuthentication().authenticate_request_token(
                token=reset_token)

            message = User.save_new_password(user_credentials, password)

            return Response(
                {'message': message},
                status=status.HTTP_202_ACCEPTED)
