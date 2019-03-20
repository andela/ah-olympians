from django.urls import path

from .views import (ArticlesAPIView, RetrieveArticleAPIView, LikeAPIView, DislikeAPIView, RateAPIView, FavouriteAPIView,
                    CommentsAPIView, RetrieveCommentsAPIView, SubCommentAPIView,LikeUnlikeAPIView, CommentDislikeAPIView)

app_name = "articles"

urlpatterns = [
    path('articles/', ArticlesAPIView.as_view()),
    path('articles/<slug>', RetrieveArticleAPIView.as_view()),
    path('rate/<slug>/', RateAPIView.as_view(), name='rate'),
    path('articles/<slug>/like', LikeAPIView.as_view()),
    path('articles/<slug>/dislike', DislikeAPIView.as_view()),
    path('articles/<slug>/comments/', CommentsAPIView.as_view()),
    path('articles/<slug>/comments/<pk>', RetrieveCommentsAPIView.as_view()),
    path('articles/<slug>/comments/<pk>/subcomment', SubCommentAPIView.as_view()),
    path('articles/<slug>/like_comment/<pk>', LikeUnlikeAPIView.as_view()),
    path('articles/<slug>/dislike_comment/<pk>', CommentDislikeAPIView.as_view()),
    path('articles/<slug>/favorite', FavouriteAPIView.as_view()),
]
