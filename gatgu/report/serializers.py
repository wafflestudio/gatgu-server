from django.contrib.auth.models import User
from rest_framework import serializers

from report.models import Report


class ReportSerializer(serializers.ModelSerializer):
    contents = serializers.CharField(required=True)
    user = serializers.SerializerMethodField()
    target_user = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = (
            'target_user',
            'user',
            'contents',
            'is_checked',
            'created_at',
            'updated_at',
        )

    def get_user(self, report):
        return report.user.id

    def get_target_user(self, report):
        return report.target_user.id
