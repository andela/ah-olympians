from rest_framework import serializers
from .models import Article
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Rate
from django.db.models import Avg


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
    rates = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

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
        fields = ['title', 'description',
                  'body', 'created_at', 'updated_at', 'slug', 'favourited','rates', 'author']
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
            'required':'rating is required'
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

