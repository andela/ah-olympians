from django.db.utils import IntegrityError
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import serializers, status
from django.db.models import Avg

from .serializers import ArticleSerializer, RateSerializer
from .models import Article, ArticleImage, ArticleLikes, Rate
from .renderer import ArticleJSONRenderer
from .serializers import ArticleSerializer


class ArticlesAPIView(APIView):
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer, )
    lookup_field = 'slug'

    def post(self, request):
        """
        creates article
        :param request: this is a request object
        :return: an http response object
        """
        context = {'request': request}
        article = request.data
        article_data = dict(article)

        serializer = self.serializer_class(data=article, context=context)
        try:
            user = request.user
            serializer.is_valid(raise_exception=True)
            article = serializer.save(author=user)
            for key, value in article_data.items():
                if key.startswith('image'):
                    image = request.data["images"]
                    article_image = ArticleImage.objects.create(
                        article=article,
                        image=image,
                        description="image for article")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            raise APIException({"warning": "the slug is already used"})

    def get(self, request):
        """
        Retrieve all articles
        """
        article = Article.objects.all()
        serializer = ArticleSerializer(article, many=True)
        return Response(serializer.data)


class RetrieveArticleAPIView(APIView):
    """
    this class that handles the get request with slug
    """

    def get(self, request, slug):
        """
        :param request: The get request being sent to the get one endpoint
        :param slug: This is the article slug
        :return: Response to the user
        """
        try:
            article = Article.objects.get(slug=slug)
            serializer = ArticleSerializer(article, many=False)
            return Response({'article': serializer.data},
                            status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"},
                status=status.HTTP_404_NOT_FOUND)

    def put(self, request, slug):
        """
        :param request: the put request for our article
        :param slug: This is the article slug(unique)
        :return: return Response
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({"error": "the article was not found"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = ArticleSerializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)

        if article.author.id == request.user.id:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            response = {"message": "unauthorised to perform the action"}
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, slug):
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise APIException('Sorry, the article was not found')

        if article.author.id == request.user.id:
            article.delete()
        else:
            response = {"message": "unauthorised to perform the action"}
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        response = {"message": "article deleted"}
        return Response(response, status=status.HTTP_202_ACCEPTED)


class RateAPIView(GenericAPIView):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get_article(self, slug):
        """
            Returns specific article using slug
        """
        article = Article.objects.all().filter(slug=slug).first()
        return article

    def get_rating(self, user, article):
        """
            Returns user article rating
        """
        try:
            return Rate.objects.get(user=user, article=article)
        except Rate.DoesNotExist:
            raise NotFound(
                detail={'rating': 'You have no rating for this article'})

    def post(self, request, slug):
        """
            Posts a rate on an article
        """
        rate = request.data
        article = self.get_article(slug)

        # check if article exists
        if not article:
            raise ValidationError(
                detail={'message': 'The article does not exist'})

        # check owner of the article
        if article.author == request.user:
            raise ValidationError(
                detail={'message': 'You cannot rate your own article'})

        # updates a user's rating if it already exists
        try:
            # Update Rating if Exists
            current_rating = Rate.objects.get(
                user=request.user.id, article=article.id)
            serializer = self.serializer_class(current_rating, data=rate)
        except Rate.DoesNotExist:
            #  Create rating if not founds
            serializer = self.serializer_class(data=rate)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, article=article)

        return Response({
            'message': 'rate_success',
            'data': serializer.data
        },
                        status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        """
            Gets articles rates
        """
        article = self.get_article(slug)
        rating = None

        # check if article exists
        if not article:
            raise ValidationError(
                detail={
                    'message':
                    'No ratings for this article because the article does not exist'
                })

        if request.user.is_authenticated:
            try:
                rating = Rate.objects.get(user=request.user, article=article)
            except Rate.DoesNotExist:
                pass

        if rating is None:
            avg = Rate.objects.filter(article=article).aggregate(
                Avg('your_rating'))

            average = avg['your_rating__avg']
            count = Rate.objects.filter(article=article.id).count()

            if avg['your_rating__avg'] is None:
                average = 0

            if request.user.is_authenticated:
                return Response({
                    'article': article.slug,
                    'average_rating': average,
                    'rate_count': count,
                    'your_rating': 'rating_not_found'
                },
                                status=status.HTTP_200_OK)
            else:
                return Response({
                    'article': article.slug,
                    'average_rating': average,
                    'rate_count': count,
                    'your_rating': 'Please login'
                },
                                status=status.HTTP_200_OK)

        serializer = self.serializer_class(rating)
        return Response({
            'message': 'successfull',
            'data': serializer.data
        },
                        status=status.HTTP_200_OK)

    def delete(self, request, slug):
        """
            Deletes a rating
        """
        article = self.get_article(slug)

        if request.user.is_authenticated:
            # check if article exists
            if not article:
                raise ValidationError(detail={'message': 'Does not exist'}, )

            elif article.author != request.user:
                # get user rating and delete
                rating = self.get_rating(user=request.user, article=article)
                rating.delete()
                return Response({'message': 'Deleted successfully'},
                                status=status.HTTP_200_OK)
            else:
                raise ValidationError(detail={'message': 'Not deleted'})


class LikeAPIView(APIView):
    """ This class proviedes a view class to like and unlike an Article
    :return: http Response mesage
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request, slug):
        """This method provides a POST view to like an article.
        :param request: http request object
        :param slug: Article slug field
        :return: http Response message
        """
        message = ArticleLikes.user_likes(request.user, slug,
                                          ArticleSerializer, 1)
        return message


class DislikeAPIView(APIView):
    """ This class proviedes a view class to like and unlike an Article
    :return: http Response mesage
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request, slug):
        """This method provides a POST view to dislike an article.
        :param request: http request object
        :param slug: Article slug field
        :return: http Response message
        """
        message = ArticleLikes.user_likes(request.user, slug,
                                          ArticleSerializer, -1)
        return message
