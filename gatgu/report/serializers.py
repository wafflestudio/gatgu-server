from django.contrib.auth.models import User
from rest_framework import serializers

from gatgu.utils import JSTimestampField
from report.models import Report



class ReportSerializer(serializers.ModelSerializer):
    report_id = serializers.ReadOnlyField(source='id')
    contents = serializers.CharField(required=True)
    reporter_id = serializers.SerializerMethodField()
    target_user_id = serializers.SerializerMethodField()
    created_at = JSTimestampField(read_only=True)
    resolved_at = JSTimestampField(read_only=True)

    class Meta:
        model = Report
        fields = (
            'report_id',
            'target_user_id',
            'reporter_id',
            'contents',
            'is_checked',
            'created_at',
            'resolved_at',
        )

    def get_reporter_id(self, report):
        return report.reporter.id

    def get_target_user_id(self, report):
        return report.target_user.id
