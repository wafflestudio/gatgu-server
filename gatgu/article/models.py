from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    writer = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, db_index=True)
    description = models.TextField(db_index=True)
    product_url = models.CharField(max_length=100)
    thumbnail_url = models.CharField(max_length=100)
    price_min = models.PositiveSmallIntegerField()
    people_count_min = models.PositiveSmallIntegerField()
    time_max = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
