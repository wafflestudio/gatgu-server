from django.urls import path, include
from rest_framework.routers import SimpleRouter

from article.views import ArticleViewSet

router = SimpleRouter()
router.register('articles', ArticleViewSet, basename='articles')  # /v1/article/

urlpatterns = [
    path('', include((router.urls))),
]