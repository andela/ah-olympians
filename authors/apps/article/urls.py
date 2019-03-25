from django.urls import path
from .views import (ArticlesAPIView, RetrieveArticleAPIView, LikeAPIView, DislikeAPIView, RateAPIView, FavouriteAPIView, CommentsAPIView,
                    RetrieveCommentsAPIView, SubCommentAPIView, LikeUnlikeAPIView, CommentDislikeAPIView, BookmarkAPIView, 
                    BookmarksAPIView, ReportArticlesView, GetSingleReportView, GetAllReportsViews, SocialShareArticle)

from .views import (ArticlesAPIView, RetrieveArticleAPIView, LikeAPIView, DislikeAPIView, RateAPIView, FavouriteAPIView, CommentsAPIView,
                    RetrieveCommentsAPIView, SubCommentAPIView, LikeUnlikeAPIView, CommentDislikeAPIView, BookmarkAPIView, BookmarksAPIView)

                    
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
    path('articles/<slug>/dislike_comment/<pk>',CommentDislikeAPIView.as_view()),
    path('articles/<slug>/favorite', FavouriteAPIView.as_view()),
    path('articles/<slug>/bookmark', BookmarkAPIView.as_view()),
    path('bookmarks/', BookmarksAPIView.as_view()),
    path('report/<slug>/',ReportArticlesView.as_view()),
    path('reports/<slug>/',GetSingleReportView.as_view()),
    path('reports/',GetAllReportsViews.as_view()),
     path("articles/<str:slug>/share/<str:provider>", SocialShareArticle.as_view() , name="share_article")
]
