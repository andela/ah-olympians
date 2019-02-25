from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView,CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User

from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend
from social_core.backends.oauth import BaseOAuth2,BaseOAuth1

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,SocialSerializer
)


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

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


    def create(self,request,*args,**kwargs):
        '''
        Fetch the access token and then create a user or
        authenticate a user
        '''

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        authenticated_user = request.user if not request.user.is_anonymous else None
        provider =  serializer.data['provider']

        strategy = load_strategy(request)
        try:
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend as error:
            return Response(
                {
                    "errors":{
                    "provider":["provider was not found",str(error)]
                }
                },status=status.HTTP_404_NOT_FOUND)
        
        if isinstance(backend,BaseOAuth1):
            token = {
                "oauth_token":serializer.data.get('access_token'),
                "oauth_token_secret":serializer.data.get('access_token_secret')
            }
            print(token)

        if isinstance(backend,BaseOAuth2):
            #Fetch the access token
            token = serializer.data['access_token']
        try:
            #check if there is an authenticated user,if true create a new one
            user = backend.do_auth(token,user=authenticated_user)
            print(user)
        except BaseException as error:
            # you cannot associate a social account with more than one user

            return Response({"errors":str(error)},status=status.HTTP_400_BAD_REQUEST
            )
        
        if user and user.is_active:
            serializer = UserSerializer(user)
            # authenticated_user_created = user.social.auth.get(provider=provider)
            # if not authenticated_user_created.extra_data['access_token']:
            #     authenticated_user_created.extra_data['access_token'] = token
            #     authenticated_user_created.save()
            
            serializer.instance = user
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response({'errors':"Social aunthentication error"},
            status=status.HTTP_400_BAD_REQUEST)
