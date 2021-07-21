from django.contrib.auth.models import User
from rest_framework import serializers

from gatgu.utils import JSTimestampField
from report.models import Report



class ReportSerializer(serializers.ModelSerializer):
    reporter_id = serializers.SerializerMethodField()
    target_user_id = serializers.SerializerMethodField()
    article_id = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = (
            'reporter_id',
            'target_user_id',
            'article_id',
            'contents',
            'is_checked',
            'created_at',
            'updated_at',
        )

    def get_reporter_id(self, report):
        return report.reporter.id

    def get_target_user_id(self, report):
        if report.target_user:
            return report.target_user.id

    def get_article_id(self, report):
        if report.article:
            return report.article.id
