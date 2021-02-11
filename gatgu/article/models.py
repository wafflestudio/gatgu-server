from django.contrib.auth.models import User
from django.db import models


class Article(models.Model):
    writer = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)
    contents = models.TextField(db_index=True)
    title = models.CharField(max_length=50, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now_add=True)


    price_min = models.CharField(max_length=10, db_index=True)
    thumbnail_url = models.ImageField(null=True)

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comment', on_delete=models.CASCADE)
    comment_writer = models.ForeignKey(User, related_name='comment', on_delete=models.CASCADE)
    contents = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class LikeArticle(models.Model):
    user = models.ForeignKey(User, related_name='like_article', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, related_name='like_article', on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('user', 'article')
        )
