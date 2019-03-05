from django.urls import path

from .views import (ArticlesAPIView, RetrieveArticleAPIView)

app_name = "articles"

urlpatterns = [
    path('articles/', ArticlesAPIView.as_view()),
    path('articles/<slug>', RetrieveArticleAPIView.as_view()),
]
