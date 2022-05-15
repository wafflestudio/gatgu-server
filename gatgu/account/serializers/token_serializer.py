from rest_framework import serializers


class TokenSerializer(serializers.BaseSerializer):
    access_token = serializers.CharField(required=True)
    refresh_token = serializers.CharField(required=True)
