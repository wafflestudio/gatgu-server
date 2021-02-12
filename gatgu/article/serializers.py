from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from user.serializers import *

from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            '__all__'
        )

    def get_userprofile(self, article):
        data = UserProfileSerializer(article.writer.userprofile, context=self.context).data
        data.pop('phone')
        try:
            return data

        except ObjectDoesNotExist:
            return serializers.ValidationError("no such user")

    def create(self, validated_data):
        return Article.objects.create(**validated_data)
