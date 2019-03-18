from django.urls import path

from .views import (ArticlesAPIView, RetrieveArticleAPIView, LikeAPIView, DislikeAPIView, RateAPIView)

app_name = "articles"

urlpatterns = [
    path('articles/', ArticlesAPIView.as_view()),
    path('articles/<slug>', RetrieveArticleAPIView.as_view()),
    path('rate/<slug>/', RateAPIView.as_view(), name='rate'),
    path('articles/<slug>/like', LikeAPIView.as_view()),
    path('articles/<slug>/dislike', DislikeAPIView.as_view()),
]
    

