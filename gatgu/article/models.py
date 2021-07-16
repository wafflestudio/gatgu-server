import datetime

from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    GATHERING = 1
    GATHERED = 2
    COMPLETED = 3
    EXPIRED = 4

    writer = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, db_index=True)

    ARTICLE_STATUS = (
        (GATHERING, "모집중"),
        (GATHERED, "모집완료"),
        (COMPLETED, "거래완료"),
        (EXPIRED, "기간만료"),
    )

    article_status = models.PositiveSmallIntegerField(choices=ARTICLE_STATUS, default=1, db_index=True)
    description = models.TextField()
    trading_place = models.CharField(max_length=50)
    product_url = models.CharField(max_length=200)
    price_min = models.PositiveIntegerField(default=0, help_text="글 작성자가 자신이 원하는 금액을 제외한 금액을 모집글에 작성한다.")
    time_in = models.DateTimeField("Date", default=datetime.date.today, help_text="7일 후를 기본값으로 가진다.")
    written_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    ordering = ['-written_at']


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    img_url = models.URLField(default="www.naver.com")
