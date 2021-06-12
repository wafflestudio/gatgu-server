import datetime

from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    writer = models.ForeignKey(User, related_name='articles', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, db_index=True)
    ARTICLE_STATUS = (
        (1, "모집중"),
        (2, "모집완료"),
        (3, "거래완료"),
        (4, "기간만료"),
    )
    article_status = models.PositiveSmallIntegerField(choices=ARTICLE_STATUS, default=1, db_index=True)
    description = models.TextField()
    trading_place = models.CharField(max_length=50)
    product_url = models.CharField(max_length=200)

    image = models.URLField(null=True)

    # 글 작성자가 자신이 원하는 금액을 제외한 금액을 모집글에 작성한다.
    price_min = models.PositiveIntegerField(default=0)

    # 현재 날짜보다 커야 하는 조건 view 에서 적용, default = 7일 후
    time_in = models.DateField("Date", default=datetime.date.today)

    written_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    ordering = ['-written_at']


class ArticleImage(models.Model):
    article = models.ForeignKey('article.Article', on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(blank=True, upload_to="img/article")


class ArticleTag(models.Model):
    TAG_01 = '식품/배달음식'
    TAG_02 = '디지털/가구/인테리어'
    TAG_03 = '육아'
    TAG_04 = '생활/화장품'
    TAG_05 = '취미'
    TAG_06 = '의류/악세사리'
    TAG_07 = '반려동물용품'
    TAG_08 = '음반/티켓/도서'
    TAG_09 = '식물'
    TAG_10 = '기타물품'

    TAG_LIST = (
        (TAG_01, '식품/배달음식'),
        (TAG_02, '디지털/가구/인테리어'),
        (TAG_03, '육아'),
        (TAG_04, '생활/화장품'),
        (TAG_05, '취미'),
        (TAG_06, '의류/악세사리'),
        (TAG_07, '반려동물용품'),
        (TAG_08, '음반/티켓/도서'),
        (TAG_09, '식물'),
        (TAG_10, '기타물품'),

    )
    article = models.ForeignKey('article.Article', on_delete=models.CASCADE, related_name='images')
    name = models.TextField(choices=TAG_LIST, blank=True)
