from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException,NotFound,ValidationError
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import serializers, status
from django.db.models import Avg

from .models import Article, ArticleImage, ArticleLikes, ArticleComment, Rate
from ..profiles.models import UserProfile
from .serializers import ArticleSerializer, CommentSerializer, DeleteCommentSerializer, RateSerializer,GetArticleSerializer
from .renderer import ArticleJSONRenderer, CommentJSONRenderer

from .renderer import ArticleJSONRenderer


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
        serializer = GetArticleSerializer(article, many=True)
        return Response(serializer.data)


    def destroy(self, request, slug):
        """
         Delete an article you have written
         :param request: The request sent
         :param slug: the slug on the url
         :return: Response
        """
        try:
            article = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise APIException('Sorry, we cannot find the article ure looking for')

        if article.author.id == request.user.profile.id:
            article.delete()
        else:
            response = {"message": "unauthorised to perform the action"}
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        response = {"message": "article deleted"}
        return Response(response, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, slug):
        """
        UPDATE an article
        :param request:
        :param slug:
        :return:
        """
        try:
            article = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            return Response({"error": "the article was not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ArticleSerializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)

        if article.author.id == request.user.profile.id:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            response = {"message": "unauthorised to perform the action"}
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


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
            serializer = GetArticleSerializer(article, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
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


class CommentVerification(object):

    def article_exists(self, slug):
        try:
            Article.objects.get(slug=slug)
        except (Exception, Article.DoesNotExist):
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException({"error": "Article does not exist!"})

        return True

    def comment_exists(self, slug, pk):
        try:
            expected_comment = ArticleComment.objects.get(
                id=pk, article=slug, is_active=True)
        except (Exception, ArticleComment.DoesNotExist):
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException({"error": "comment does not exist!"})

        return expected_comment

    def check_permision(self, owner, requester):
        if owner != requester:
            APIException.status_code = status.HTTP_403_FORBIDDEN
            raise APIException(
                {"error": "You do not have that permission on this comment!"})

        return True

    def check_profile(self, user_id):
        try:
            UserProfile.objects.get(username_id=user_id, active_profile=True)
        except UserProfile.DoesNotExist:
            APIException.status_code = status.HTTP_403_FORBIDDEN
            raise APIException(
                {"error": "Permission denied! You don't have a profile"})


class CommentsAPIView(APIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer

    def post(self, request, slug):
        CommentVerification.check_profile(self, request.user.id)
        CommentVerification.article_exists(self, slug)
        new_comment = request.data.get('comment', {})

        new_comment["article"] = slug

        serializer = self.serializer_class(data=new_comment)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user.profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        CommentVerification.article_exists(self, slug)

        serializer = self.serializer_class(ArticleComment.objects.filter(
            article=slug, parent_comment=None), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveCommentsAPIView(APIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer

    def get(self, request, **kwargs):
        serializer = self.serializer_class(
            CommentVerification.comment_exists(self, kwargs['slug'], kwargs['pk']))

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, **kwargs):
        CommentVerification.check_profile(self, request.user.id)
        update_comment = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])

        CommentVerification.check_permision(
            self, update_comment.author, request.user.profile)

        updated_data = request.data.get('comment', {})
        serializer = CommentSerializer(
            update_comment, data=updated_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        CommentVerification.check_profile(self, request.user.id)
        delete_comment = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])

        CommentVerification.check_permision(
            self, delete_comment.author, request.user.profile)

        serializer = DeleteCommentSerializer(
            delete_comment, data={"is_active": False})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class SubCommentAPIView(APIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer

    def post(self, request, **kwargs):
        CommentVerification.check_profile(self, request.user.id)
        new_comment = request.data.get('comment', {})

        parent_article = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])

        new_comment["article"] = kwargs['slug']

        serializer = self.serializer_class(data=new_comment)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user.profile,
                        parent_comment=parent_article)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, **kwargs):
        CommentVerification.comment_exists(self, kwargs['slug'], kwargs['pk'])

        serializer = self.serializer_class(ArticleComment.objects.filter(
            article=kwargs['slug'], parent_comment=kwargs['pk']), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
