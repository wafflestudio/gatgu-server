from django.contrib.auth.models import User
from django.db import models

from article.models import Article


class Report(models.Model):
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_reports',
                                    null=True, blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reports',
                                null=True, blank=True)
    contents = models.TextField()
    is_checked = models.BooleanField(default=False, help_text="신고 상황 종료 시 True")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reporter}'s"
