import uuid
import os

from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models
from rest_framework import exceptions
import jwt

from .utils import send_email


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, username, email, password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a `User` with superuser powers.
        Superuser powers means that this use is an admin that can do anything
        they want.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True)

    # When a user no longer wishes to use our platform, they may try to delete
    # there account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. To solve this problem, we
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users, this flag will always be
    # falsed.
    is_staff = models.BooleanField(default=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    # More fields required by Django when specifying a custom user model.

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case, we want that to be the email field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.
        This string is used when a `User` is printed in the console.
        """
        return self.email

    def token(self, days=60):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().
        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token(days)

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.username

    def _generate_jwt_token(self, days):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    def create_token(self):
        """
        This
        :return:
        """
        token = str(uuid.uuid4())
        verification = EmailVerification.objects.create(user=self, token=token)
        verification.save()
        return verification.token

    @staticmethod
    def send_reset_token(serializer, request):
        """This method sends a reset token through email.
        Takes in a serializer and request objects as parameters
        :param serializer:
        :param request:
        :return: message
        """
        subject = "Email verification"
        message = "If we found an account; we've emailed you a link to change your password. " \
                  "Please check your email (and spam folder)"

        if serializer.is_valid(raise_exception=True):
            try:
                user = User.objects.get(email=request.data['email'])
                no_of_requests = PasswordTokenReset.check_request_times(user.id)

                if no_of_requests < 5:
                    token = user.token(1)
                    user.save_reset_token(user, token)
                    req_message = User.generate_link_message(token)

                    x = send_email(
                        to_email=user.email,
                        subject=subject,
                        message=req_message)
                    return message
                else:
                    return "Too many password requests made in the last 24 hrs." \
                           "Please wait for 24 hours to make another reset request"
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed(message)

    def save_reset_token(self, user, tkn):
        """This method takes a token and saves it to database
        Takes a user object and token as parameters
        :param user:
        :param tkn:
        :return: none
        """
        reset_tkn = PasswordTokenReset.objects.create(user=user, token=tkn)
        reset_tkn.save()
        # return reset_tkn

    @staticmethod
    def generate_link_message(token):
        """This method takes in a token and generates a link to be
        sent to a user on a password reset request.
        Takes in a token as a parameter
        :param token:
        :return: Returns a message with a url link
        """
        link = "{}api/users/reset_password/{}".format(os.environ['URL'], token)

        request_message = "An account associated with this email address " \
                          "for Authors Haven has requested a password reset." \
                          " If you did, click on the given link" \
                          " \n {} \notherwise ignore this email. ".format(link)
        return request_message

    @staticmethod
    def save_new_password(user_credentials, password):
        """This method takes in a token verifies it and resets users password
        :param user_credentials: details of user resetting password
        :return: successful password reset
        """
        new_password = password
        user = user_credentials[0]
        user.set_password(new_password)
        user.save()
        return 'Password reset successful.' \
               'You may now log in with the new credentials'


class EmailVerification(models.Model):
    """
    This class creates a Password Reset Token.
    """
    user = models.ForeignKey(
        User,
        related_name='email_verifications',
        on_delete=models.CASCADE,
        verbose_name='User associated with this email token'
    )
    token = models.CharField(max_length=256)
    created = models.DateTimeField(
        auto_now=True,
        verbose_name='When was this TOKEN created'
    )
    is_valid = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)


class PasswordTokenReset(models.Model):
    """
    This class creates a Password Reset Token model.
    """

    user = models.ForeignKey(
        User,
        related_name='reset_password_tokens',
        on_delete=models.CASCADE,
        verbose_name='User associated with this reset token'
    )
    token = models.CharField(max_length=256)
    created = models.DateTimeField(
        auto_now=True,
        verbose_name='When was this TOKEN created'
    )

    class Meta:
        ordering = ('created',)

    @staticmethod
    def check_request_times(user_id):
        """This method checks the number of password reset requests a
        user has made in a given day
        :return: number of requests a user has made ia day
        """
        today = date.today()
        no = PasswordTokenReset.objects.filter(
            user=user_id, created__contains=today).count()
        return no
