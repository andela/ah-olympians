from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from rest_framework import serializers

from rest_framework import response

from authors.apps.authentication.serializers import UserSerializer
from .models import Article, ArticleLikes, Rate,ArticleComment
from ..profiles.serializers import ProfileSerializer


class LikesSerializer(serializers.ModelSerializer):
    """
    This class serializes data from ArticleLikes model
    """
    user = UserSerializer()

    class Meta:
        model = ArticleLikes
        fields = ('user',)


class TagSerializer(serializers.Field):
    """
    tag serializer class
    """
    def to_internal_value(self, data):
       
        tag_data = ArticleSerializer().validate_tag_list(data)
        return tag_data
    
    def to_representation(self,obj):
        """
        converts taggable manager instance to a list
        """
        if type(obj) is not list:
            return [tag for tag in obj.all()]
        return obj
     

class ArticleSerializer(serializers.ModelSerializer):
    """
    converts the model into JSON format
    """

    author = UserSerializer(read_only=True)
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    tag_list = TagSerializer(default=[])

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


    def validate_tag_list(self, validated_data):
        if type(validated_data) is not list:
            raise serializers.ValidationError(
                {"message":"error"}
            )
        
        for tag in validated_data:
            if not isinstance(tag,str):
                raise serializers.ValidationError(
                    {"message":"error"}
                )
            return validated_data
    
    def create(self,validated_data,*args):
        """
        post saves tags after the article has been saved
        """
        article = Article(**validated_data)
        article.save()
        tags_to = Article.objects.get(pk=article.pk)

        if article.tag_list is not None:
            for tag in article.tag_list: 
                tags_to.tag_list.add(tag)

            return article
        article.tag_list = []
        return article
    
    def update(self,instance,validated_data):
        """
        update the tag_list field
        """
        if 'tag_list' not in validated_data:
            return instance
        
        tag_list = validated_data.pop('tag_list',None)

        validated_data.pop('slug',None)

        for (key,value) in validated_data.items():
            setattr(instance,key,value)

        instance.tag_list.set(*tag_list,clear=True)
        instance.save()

        instance.tag_list = tag_list
        return instance

    class Meta:
        model = Article
        fields = [
            'title',
            'description',
            'tag_list',
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


class SubcommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = ArticleComment
        fields = ['id', 'article', 'createdAt', 'updatedAt',
                  'body', 'author', 'is_active', 'subcomments']


class CommentSerializer(serializers.ModelSerializer):
    """
    converts the model into JSON format
    """
    subcomments = SubcommentSerializer(many=True, read_only=True)
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = ArticleComment
        fields = ['id', 'article', 'createdAt', 'updatedAt',
                  'body', 'author', 'is_active', 'subcomments']


class DeleteCommentSerializer(serializers.ModelSerializer):
    """
    converts the model into JSON format
    """
    class Meta:
        model = ArticleComment
        fields = ['is_active']

class GetArticleSerializer(serializers.ModelSerializer):
    tag_list = serializers.SerializerMethodField()
    
    def get_tag_list(self,article):
        return list(article.tag_list.names())

    class Meta:
        model = Article
        fields = '__all__'

class GetArticleLikesSerializer(serializers.ModelSerializer):
    tag_list = serializers.SerializerMethodField()
    
    def get_tag_list(self,article):
        return list(article.tag_list.names())

    class Meta:
        model = ArticleLikes
        fields = '__all__'
