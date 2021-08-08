# def hello_every_minite():
#     print('Hello')
import datetime

from rest_framework import status
from rest_framework.response import Response

from article.models import Article


def article_status():
    articles = Article.objects.all()
    expired_article = articles.filter(time_in__lt=datetime.date.today())
    if expired_article and expired_article.get('article_status') == 1:
        expired_article.update(article_status=4)

    gathering_article = articles.filter(time_in__gte=datetime.date.today())
    if gathering_article and gathering_article.get('article_status') == 4:
        gathering_article.update(article_status=1)

    return Response({"message": "Successfully updated the status of articles"}, status=status.HTTP_200_OK)
