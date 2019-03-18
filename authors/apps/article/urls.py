from django.urls import path
from .views import (ArticlesAPIView, RetrieveArticleAPIView, RateAPIView)
app_name = "articles"

urlpatterns = [
    path('articles/', ArticlesAPIView.as_view()),
    path('articles/<slug>', RetrieveArticleAPIView.as_view()),
    path('rate/<slug>/', RateAPIView.as_view(), name='rate'),

]
    

