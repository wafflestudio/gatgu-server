from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    writer = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=50)
    product_url = models.URLField()
    thumbnail = models.URLField(null=True)
    image = models.URLField(null=True)
    people_min = models.PositiveSmallIntegerField()
    price_min = models.PositiveIntegerField()


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

    written_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    NEED_TYPE = (
        (1, 'people'),
        (2, 'money'),
    )

    need_type = models.PositiveSmallIntegerField(choices=NEED_TYPE, default=1, null=True)

    ordering = ['-written_at']
