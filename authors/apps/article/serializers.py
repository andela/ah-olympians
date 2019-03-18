from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from rest_framework import serializers

from authors.apps.authentication.serializers import UserSerializer
from .models import Article, ArticleLikes
from .models import Rate


class LikesSerializer(serializers.ModelSerializer):
    """
    This class serializes data from ArticleLikes model
    """
    user = UserSerializer()

    class Meta:
        model = ArticleLikes
        fields = ('user',)


class ArticleSerializer(serializers.ModelSerializer):
    """
    converts the model into JSON format
    """
    author = UserSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    def get_rates(self, obj):
        """
            Returns rating average
        """
        average = Rate.objects.filter(
            article__pk=obj.pk).aggregate(Avg('your_rating'))

        if average['your_rating__avg'] is None:
            average_rating = 0
            return average_rating

        return average['your_rating__avg']

    class Meta:
        model = Article

        fields = [
            'title',
            'description',
            'body',
            'created_at',
            'updated_at',
            'slug',
            'favourited',
            'author',
            'likes_count',
            'dislikes_count',
            'likes',
            'dislikes',
        ]

    def get_likes(self, obj):
        """
        This method returns users who liked an Article
        :param obj: This is the Article object
        :return: users who liked an article
        """
        query = obj.liked.filter(likes=1)
        return LikesSerializer(query, many=True).data

    def get_dislikes(self, obj):
        """
        This method returns users who disliked an Article
        :param obj: This is the Article object
        :return: users who liked an article
        """
        query = obj.liked.filter(dislikes=-1)
        return LikesSerializer(query, many=True).data

    def get_likes_count(self, obj):
        """
        This method returns number of users who liked an Article
        :param obj: This is the Article object
        :return: count of users who liked an article
        """
        return obj.liked.filter(likes=1).count()

    def get_dislikes_count(self, obj):
        """
        This method returns number of users who disliked an Article
        :param obj: This is the Article object
        :return: count of users who disliked an article
        """
        return obj.liked.filter(dislikes=-1).count()


class RateSerializer(serializers.ModelSerializer):
    """
        Rating model serializers
    """
    max_rate = 5
    min_rate = 1
    your_rating = serializers.IntegerField(
        required=True,
        validators=[
            MinValueValidator(
                min_rate,
                message='You cannot rate below 1'
            ),
            MaxValueValidator(
                max_rate,
                message='You cannot rate above 5'
            )
        ],
        error_messages={
            'required': 'rating is required'
        }
    )
    article = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    rate_count = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        """
            Returns rating average
        """
        average = Rate.objects.filter(
            article=obj.article.id).aggregate(Avg('your_rating'))
        return average['your_rating__avg']

    def get_article(self, obj):
        """
            Gets article slug
        """
        return obj.article.slug

    def get_rate_count(self, obj):
        """
            Gets article rate count
        """
        count = Rate.objects.filter(
            article=obj.article.id).count()
        return count

    class Meta:
        model = Rate
        fields = ('article', 'average_rating', 'rate_count', 'your_rating')
