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

    # 현재 날짜보다 커야 하는 조건 추가
    time_in = models.DateField("Date", default=datetime.date.today, help_text="7일 후를 기본값으로 가진다.")
    written_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    ordering = ['-written_at']


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    img_url = models.URLField(blank=True)


class Tag(models.Model):
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
    name = models.CharField(choices=TAG_LIST, blank=True, max_length=20, null=True)


class ArticleTag(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tags', null=True, blank=True, max_length=50)

    class Meta:
        unique_together = (
            ('article', 'tag')
        )
