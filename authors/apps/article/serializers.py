from rest_framework import serializers
from .models import Article

from authors.apps.authentication.serializers import UserSerializer


class ArticleSerializer(serializers.ModelSerializer):
    """
    converts the model into JSON format
    """

    title = serializers.CharField(required=True)
    slug = serializers.SlugField(required=False)
    description = serializers.CharField(required=True)
    body = serializers.CharField(required=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    favourited = serializers.BooleanField(required=False)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['title', 'description',
                  'body', 'created_at', 'updated_at', 'slug', 'favourited', 'author']

