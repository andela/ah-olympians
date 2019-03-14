from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

from .models import Article, ArticleImage
from .serializers import ArticleSerializer
from .renderer import ArticleJSONRenderer


class ArticlesAPIView(APIView):
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer,)
    lookup_field = 'slug'

    def post(self, request):
        """
        creates article
        :param request: this is a request object
        :return: an http response object
        """
        context = {
            'request': request
        }
        article = request.data
        article_data = dict(article)

        serializer = self.serializer_class(
            data=article, context=context
        )
        try:
            user = request.user
            serializer.is_valid(raise_exception=True)
            article = serializer.save(author=user)
            for key, value in article_data.items():
                if key.startswith('image'):
                    image = request.data["images"]
                    article_image = ArticleImage.objects.create(article=article, image=image,
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            return Response({"message": "The article requested does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, slug):
        """
        :param request: the put request for our article
        :param slug: This is the article slug(unique)
        :return: return Response
        """
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response({"error": "the article was not found"}, status=status.HTTP_404_NOT_FOUND)
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
