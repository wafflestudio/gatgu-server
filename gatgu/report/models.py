from django.contrib.auth.models import User
from django.db import models

from article.models import Article


class Report(models.Model):
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    contents = models.TextField()
    is_checked = models.BooleanField(default=False, help_text="신고 상황 종료 시 True")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s"


class ReportComment(models.Model):
    # 신고자 또는 관리자 가 Report 에 다는 댓글
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='report_comments')
    report = models.ForeignKey('report.Report', on_delete=models.CASCADE, related_name='comments')
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.report}'s by {self.user}"
