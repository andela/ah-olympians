from cloudinary.models import CloudinaryField
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from cloudinary.models import CloudinaryField
from taggit.managers import TaggableManager

from authors.apps.authentication.models import User
from ..profiles.models import UserProfile


# Create your models here.
class Article(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favourited = models.BooleanField(default=False)
    author = models.ForeignKey(
        User, related_name="articles", on_delete=models.CASCADE)
    tag_list = TaggableManager(blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("articles:articles", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            """
            creating slug
            """
            a_slug = slugify(self.title)
            origin = 1
            unique_slug = a_slug
            while Article.objects.filter(slug=unique_slug).exists():
                unique_slug = '{}-{}'.format(a_slug, origin)
                origin += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article,
        related_name='article_images',
        on_delete=models.CASCADE,
        verbose_name='Image associated with the article')
    image = CloudinaryField(
        'image', default="image/upload/v1551960935/books.png")
    created = models.DateTimeField(
        auto_now=True, verbose_name='When was this image saved')
    description = models.CharField(db_index=True, max_length=255)

    class Meta:
        ordering = ('created',)


class Rate(models.Model):
    """
        Rate model schema
    """
    user = models.ForeignKey(
        User,
        related_name="rater",
        on_delete=models.CASCADE)

    article = models.ForeignKey(
        Article,
        related_name='rated_article',
        on_delete=models.CASCADE
    )

    your_rating = models.FloatField(null=False)


class ArticleLikes(models.Model):
    """This class creates a model for Article likes and dislikes"""
    user = models.ForeignKey(
        User, related_name='liked_by', on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article,
        to_field='slug',
        db_column='article',
        on_delete=models.CASCADE,
        related_name='liked')
    likes = models.IntegerField(null=True)
    dislikes = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created',)

    @staticmethod
    def get_article(slug):
        """ This method gets a single Article
        :param slug: The Article's unique slug
        :return: returns a serialized Article
        """
        article = get_object_or_404(Article, slug=slug)
        return article

    @staticmethod
    def user_likes(user, slug, ArticleSerializer, value):
        """This method creates an Article like or dislike.
        :param user: The user liking or disliking an Article
        :param slug: The Article unique slug
        :param value: The value for like or dislike.
                      Takes in a +1 for like or -1 for dislike.
        :return: success message or fail
        """
        try:
            likes = ArticleLikes.objects.filter(user=user, article=slug)
            article = ArticleLikes.get_article(slug=slug)
        except:
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException(
                {'article': {
                    'message': 'Article requested does not exist'
                }})
        if not likes:
            if value == 1:
                ArticleLikes.objects.create(
                    user=user, article=article, likes=value)
                return Response(
                    {'message': 'Successfully liked: {} article'.format(slug),
                     'article': ArticleSerializer(article).data},
                    status=status.HTTP_201_CREATED)
            ArticleLikes.objects.create(
                user=user, article=article, dislikes=value)
            return Response(
                {'message': 'Successfully disliked: {} article'.format(slug),
                 'article': ArticleSerializer(article).data},
                status=status.HTTP_201_CREATED)
        likes.delete()
        return Response({
            'message':
                'Successfully undid (dis)like on {} article'.format(slug),
            'article': ArticleSerializer(article).data
        }, status=status.HTTP_202_ACCEPTED)
        
class ArticleComment(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    article = models.ForeignKey(
        Article, related_name="comments", on_delete=models.CASCADE, to_field="slug")
    parent_comment = models.ForeignKey(
        'self', related_name='subcomments',  on_delete=models.CASCADE, blank=True, null=True)
    body = models.TextField(blank=False)
    author = models.ForeignKey(
        UserProfile, related_name="comments", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('createdAt',)

    def __str__(self):
        return self.body[:20]
