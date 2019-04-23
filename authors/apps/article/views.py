from django.db.models import Avg
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import strip_tags
from django_social_share.templatetags import social_share


from rest_framework import status
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from ..authentication.models import User
from ..authentication.utils import send_email
from .models import(
    Article, ArticleImage, ArticleLikes, Rate,
    ArticleFavourite, ArticleComment, LikeComment, ArticleBookmark,
    ReportArticle
    )
from ..profiles.models import UserProfile, NotifyMe
from ..profiles.serializers import NotificationSerializer
from .renderer import ArticleJSONRenderer, CommentJSONRenderer
from .serializers import(
    ArticleSerializer, CommentSerializer, DeleteCommentSerializer,
    RateSerializer, BookmarksSerializer, ReportSerializer
    )
from .utils import email_message


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

        CommentVerification().check_profile(self.request.user.id)

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


            # Start of notification sending
            queryset = user.profile.following.all()
            queryset = queryset.filter(email_notify=True)
            serializer2 = NotificationSerializer(queryset, many=True)

            my_list = list()
            for i in range(len(serializer2.data)):
                my_list.append(serializer2.data[i]["username"])

            author_name = serializer.data["author"]["username"]
            article_title = serializer.data["title"]
            subject = "A new article from {}".format(author_name)
            send_email(
                my_list, subject,
                "A user you follow posted a new article. You can read it \
                via this URL https://aholympian.herokuapp.com/api/articles/{}".format(serializer.data["slug"]))

            NotifyMe.objects.create(
                username=user,
                notification="A new article titled {} from {}".format(article_title, author_name),
                slug=serializer.data["slug"])

            # End of notification sending

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            raise APIException({"warning": "the slug is already used"})

    def get(self, request):
        """
        Retrieve all articles
        """
        articles = Article.objects.all()
        for article in articles:
            article.tag_list = list(article.tag_list.names())
        serializer = ArticleSerializer(
            articles, many=True, context={'request': self.request})
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
            raise APIException(
                'Sorry, we cannot find the article ure looking for')

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
            return Response({"error": "the article was not found"},
                            status=status.HTTP_404_NOT_FOUND)
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
            article.tag_list = list(article.tag_list.names())
            serializer = ArticleSerializer(
                article, many=False, context={'request': self.request})
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
        serializer = ArticleSerializer(
            article, data=request.data, context={'request': self.request})
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
            article = Article.objects.get(slug=slug)
        except (Exception, Article.DoesNotExist):
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException({"error": "Article does not exist!"})

        return article

    def get_article_id(self, slug):
        article = Article.objects.get(slug=slug).id
        return article

    def get_article_title(self, slug):
        article = Article.objects.get(slug=slug).title
        return article

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

    def check_like(self, serial_data, profile_id, comment_id):
        if LikeComment.get_like_status(profile_id, comment_id,
                                       'like') != False:
            serial_data['like'] = True
        if LikeComment.get_like_status(profile_id, comment_id,
                                       'dislike') != False:
            serial_data['dislike'] = True

        if 'subcomments' in serial_data:
            if len(serial_data['subcomments']) > 0:
                for return_data in serial_data['subcomments']:
                    return_data = CommentVerification.check_like(
                        self, return_data, profile_id, return_data['id'])

        return serial_data


class CommentsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CommentJSONRenderer, )
    serializer_class = CommentSerializer

    def post(self, request, slug):
        CommentVerification.check_profile(self, request.user.id)
        CommentVerification.article_exists(self, slug)
        article_id = CommentVerification.get_article_id(self, slug)
        article_title = CommentVerification.get_article_title(self, slug)
        new_comment = request.data.get('comment', {})

        new_comment["article"] = slug

        serializer = self.serializer_class(
            data=new_comment, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user.profile)


        # Start of notification sending
        comment_author = request.user.profile.username.username
        NotifyMe.objects.create(
            article_id=article_id,
            notification="A new comment from {} on the article ({}) \
            that you favorited".format(comment_author, article_title),
            title="New Comment")
        #End of notification sending

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        CommentVerification.article_exists(self, slug)

        serializer = self.serializer_class(
            ArticleComment.objects.filter(article=slug, parent_comment=None),
            many=True,
            context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveCommentsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CommentJSONRenderer, )
    serializer_class = CommentSerializer

    def get(self, request, **kwargs):
        get_comment = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])
        serializer = self.serializer_class(
            get_comment, context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, **kwargs):
        CommentVerification.check_profile(self, request.user.id)
        update_comment = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])

        CommentVerification.check_permision(self, update_comment.author,
                                            request.user.profile)

        updated_data = request.data.get('comment', {})
        serializer = CommentSerializer(
            update_comment,
            data=updated_data,
            partial=True,
            context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        CommentVerification.check_profile(self, request.user.id)
        delete_comment = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])

        CommentVerification.check_permision(self, delete_comment.author,
                                            request.user.profile)

        serializer = DeleteCommentSerializer(
            delete_comment, data={"is_active": False})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "comment deleted successfully"},
                        status=status.HTTP_202_ACCEPTED)


class SubCommentAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CommentJSONRenderer, )
    serializer_class = CommentSerializer

    def post(self, request, **kwargs):
        CommentVerification.check_profile(self, request.user.id)
        new_comment = request.data.get('comment', {})

        parent_article = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])

        new_comment["article"] = kwargs['slug']

        serializer = self.serializer_class(
            data=new_comment, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=request.user.profile, parent_comment=parent_article)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, **kwargs):
        CommentVerification.comment_exists(self, kwargs['slug'], kwargs['pk'])

        serializer = self.serializer_class(
            ArticleComment.objects.filter(
                article=kwargs['slug'], parent_comment=kwargs['pk']),
            many=True,
            context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class LikeUnlikeAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CommentJSONRenderer, )

    def post(self, request, **kwargs):
        CommentVerification.check_profile(self, request.user.id)
        like_comment = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])

        return_message = LikeComment.comment_like_unlike(
            request.user.profile, like_comment.id)

        return Response(return_message, status=status.HTTP_200_OK)


class CommentDislikeAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CommentJSONRenderer, )

    def post(self, request, **kwargs):
        CommentVerification.check_profile(self, request.user.id)
        like_comment = CommentVerification.comment_exists(
            self, kwargs['slug'], kwargs['pk'])

        return_message = LikeComment.comment_dislike(request.user.profile,
                                                     like_comment.id)

        return Response(return_message, status=status.HTTP_200_OK)


class FavouriteAPIView(APIView):
    """
    This class favourites an article
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request, slug):
        """
        This is the post method that favourites an article
        :param request:
        :param slug:
        :return:
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            response = {
                "message":
                "You can not favourite this article because it doesn't exist"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        try:
            favourited = ArticleFavourite.objects.get(
                user=request.user, article=article)
            return Response(
                {"error": "you have already favourited the article"},
                status=status.HTTP_406_NOT_ACCEPTABLE)

        except ArticleFavourite.DoesNotExist:
            favourited = ArticleFavourite.objects.create(
                user=request.user, article=article, favourited=True)
            response = {"message": "Successfully favourited the article"}
            return Response(response, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, slug):
        """
        This is the delete method that favourites an article
        :param request:
        :param slug:
        :return:
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            response = {"message": "You can not favourite this article"}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        try:
            favourited = ArticleFavourite.objects.get(
                user=request.user, article=article)
            article = ArticleFavourite.objects.get(
                user=request.user, article=article, favourited=True)
            article.delete()
            return Response({"success": "you have successfully deleted"},
                            status=status.HTTP_202_ACCEPTED)

        except ArticleFavourite.DoesNotExist:
            return Response({"error": "you have not favourited this article"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)


class BookmarkAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, slug):
        CommentVerification.check_profile(self, request.user.id)
        article = CommentVerification.article_exists(self, slug)

        return_data = ArticleBookmark.create_bookmark(request.user, article)
        return_message = {}

        if 'error' in return_data:
            return_message = Response(
                return_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return_message = Response(
                return_data, status=status.HTTP_201_CREATED)

        return return_message

    def delete(self, request, slug):
        CommentVerification.check_profile(self, request.user.id)
        CommentVerification.article_exists(self, slug)

        return_data = ArticleBookmark.remove_bookmark(request.user.id, slug)
        return_message = {}

        if 'error' in return_data:
            return_message = Response(
                return_data, status=status.HTTP_404_NOT_FOUND)
        else:
            return_message = Response(
                return_data, status=status.HTTP_202_ACCEPTED)

        return return_message


class BookmarksAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = BookmarksSerializer

    def get(self, request):
        CommentVerification.check_profile(self, request.user.id)

        articles = ArticleBookmark.objects.filter(user=request.user.id)
        for bookmark in articles:
            bookmark.article.tag_list = list(bookmark.article.tag_list.names())

        serializer = self.serializer_class(articles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportArticlesView(ListCreateAPIView):
    queryset = ReportArticle.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsAuthenticated, )

    def get_article(self, slug):
        """
            Returns specific article using slug
        """

        try:
            article = Article.objects.get(slug=slug)

            return article
        except:
            return "error"

    def post(self, request, slug):
        """Checks if there is an article with that slug"""
        article = self.get_article(slug)
        if article == "error":
            error_message = {
                "error_message": "The article you are reporting does not exist"
            }
            return Response(error_message)
        else:
            if article.author == request.user:
                return Response(
                    {"errors": "You cannot report your own article"},
                    status=status.HTTP_400_BAD_REQUEST)
            """gets the article, report_message and reader"""
            article_reported = article
            report_message = request.data.get('report_message', {})
            reader_report = request.user

            no_of_reports = ReportArticle.objects.filter(
                article=article_reported, reader=reader_report).count()
            """checks if the reader has reported the article more than once"""
            if no_of_reports >= 1:
                return Response(
                    {"errors": "You can only report an article once"},
                    status=status.HTTP_400_BAD_REQUEST)
            report = {
                'article': article.slug,
                'report_message': report_message,
                'reader': request.user
            }
            """A sample report"""
            serializer = self.serializer_class(data=report)
            serializer.is_valid(raise_exception=True)
            content = "Your report has been sent successfully to the admin "
            response_message = {"message": content}
            email_address = "andelaolympians@gmail.com"
            subject = "Article Reports"
            message = email_message(article.slug, report_message)
            mail_sent = send_email(email_address, subject, message)
            serializer.save()
            return Response(response_message, status=status.HTTP_200_OK)


class GetSingleReportView(RetrieveAPIView):
    queryset = ReportArticle.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request, slug):
        """
            Returns specific article using slug
        """
        if not request.user.is_superuser:
            return Response({"message": "You have no permissions"},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:
            article = Article.objects.get(slug=slug)
            report = ReportArticle.objects.get(article=article)

        except Exception as e:
            return Response({"message": "error" + str(e)},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(report)

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAllReportsViews(RetrieveAPIView):
    queryset = ReportArticle.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        """
            Returns specific article using slug
        """
        if not request.user.is_superuser:
            return Response({"message": "You have no permissions"},
                            status=status.HTTP_401_UNAUTHORIZED)

        reports = ReportArticle.objects.all()
        if len(reports) == 0:
            return Response({"message": "No reports"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialShareArticle(RetrieveAPIView):
    '''
    handle social sharing of an article by an authenticated user
    '''

    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        '''
        return a sharable link if you are an authenticated user and 
        enable the user to redirect to the specified url
        '''

        # fetch provider specified in the url
        provider = kwargs['provider']

        context = {'request': request}

        # try fetch an article using the provided slug from the database
        # if the article does not exist return 404 not found

        try:
            article = Article.objects.get(slug=kwargs['slug'])

        except Article.DoesNotExist:
            raise NotFound({"error": "article was not found"})

        article_url = request.build_absolute_uri("{}article/{}".format(
            article.slug, provider))

        share_link = self.get_link(context, provider, article, article_url)

        if not share_link:
            # where provider is invalid,return a provider invalid error
            return Response({"error": "provider was invalid"})

        return Response({"share": {
            "link": share_link,
            "provider": provider
        }}, status.HTTP_200_OK)

    def get_link(self, context, provider, article, article_url):
        share_link = None

        if provider == "facebook":
            # get link to redirect for a facebook share

            share_link = social_share.post_to_facebook_url(
                context, article_url)['facebook_url']

        elif provider == "twitter":
            text = "Read this on Authors Heaven: {}".format(article.title)

            share_link = social_share.post_to_twitter(
                context,
                text,
                article_url,
                link_text='Post this article to twitter')['tweet_url']

        elif provider == 'reddit':
            # share link to reddit platform
            share_link = social_share.post_to_reddit_url(
                context, article.title, article_url)['reddit_url']

        elif provider == 'linkedin':
            title = 'Check this article out on Authors Heaven {}'.format(
                article.title)

            # This gets the sharable link for an article to redirect to the linkedin platform

            share_link = social_share.post_to_linkedin_url(
                context, title, article_url)['linkedin_url']

        elif provider == "email":
            subtitle = "Wow!An article from Authors Heaven has been shared to you!Read!!"

            # get share link for user to redirect to the email platform
            share_link = social_share.send_email_url(
                context,
                subtitle,
                article_url,
            )['mailto_url']

        return share_link


class SearchArticles(APIView):
    """This class creates a view to perform search and filtering on articles.
    :returns: a http Response message
    """

    def get(self, request):
        """This method creates a GET APIView to search for or filter Articles
        :params request: this is the HTTP request object
        :returns: Returns a HTTP Response object
        """

        query_params = dict(request.GET.items())
        if not query_params:
            return Response({'message': 'Please provide a search phrase'},
                            status=status.HTTP_400_BAD_REQUEST)

        query_params_values = list(query_params.values())
        query = Article().search_articles(query_params_values)

        if not query:
            return Response({
                'message':
                'Sorry we could not find what you are looking for.'
            },
                            status=status.HTTP_404_NOT_FOUND)

        for article in query:
            article.tag_list = list(article.tag_list.names())
        serializer = ArticleSerializer(query, many=True)
        return Response({'article': serializer.data},
                        status=status.HTTP_200_OK)
