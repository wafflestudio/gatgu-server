from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):

    writer = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=50)
    product_url = models.URLField()
    thumbnail_url = models.URLField()
    image = models.URLField(null=True)
    people_min = models.PositiveSmallIntegerField()
    price_min = models.PositiveIntegerField()
    time_in = models.DurationField(null=True)
    tag = models.PositiveSmallIntegerField(null=True)
    '''tag list to be added
    TAG = (
        (1, '...'),
        (2, '...'),
        
    )
    '''
    tag_used_count = models.PositiveIntegerField(default=0)

    written_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    NEED_TYPE = (
        (1, 'people'),
        (2, 'money'),
    )

    need_type = models.PositiveSmallIntegerField(choices=NEED_TYPE, default=1, null=True)

    ordering = ['-written_at']
