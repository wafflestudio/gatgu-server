from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    writer = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
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
    product_url = models.URLField()
    image = models.URLField(null=True)

    # 글 작성자가 자신이 원하는 금액을 제외한 금액을 모집글에 작성한다.
    price_min = models.PositiveIntegerField(default=0)

    TAG_LIST = (
        (1, '식품/배달음식'),
        (2, '디지털/가구/인테리어'),
        (3, '육아'),
        (4, '생활/화장품'),
        (5, '취미'),
        (6, '의류/악세사리'),
        (7, '반려동물용품'),
        (8, '음반/티켓/도서'),
        (9, '식물'),
        (10, '기타물품'),

    )

    tag = models.PositiveSmallIntegerField(choices=TAG_LIST, null=True)

    # 현재 날짜보다 커야 하는 조건 view 에서 적용
    time_in = models.DateField(null=True)

    written_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    ordering = ['-written_at']
