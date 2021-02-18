from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    writer = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, db_index=True)
    description = models.TextField(db_index=True)
    location = models.CharField(max_length=50)
    product_url = models.CharField(max_length=100)
    thumbnail_url = models.CharField(max_length=100)
    people_count_min = models.PositiveSmallIntegerField()
    price_min = models.PositiveSmallIntegerField()
    time_max = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    NEED_TYPE = (
        (1, 'people'),
        (2, 'money'),
    )

    need_type = models.PositiveSmallIntegerField(choices=NEED_TYPE, default=1, null=True)

    class Meta:
        ordering = ["-created_at"]
