from django.db.models import Sum
from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from user.serializers import *

from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    deleted_at = serializers.DateTimeField(read_only=True)
    need_type = serializers.ChoiceField(Article.NEED_TYPE)
    people_min = serializers.IntegerField(required=True)
    price_min = serializers.IntegerField(required=True)
    # participant_count = serializers.SerializerMethodField
    # current_price = serializers.SerializerMethodField

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'description',
            'location',
            'product_url',
            'thumbnail_url',
            'need_type',
            'people_min',
            'price_min',
            'time_in',
            'written_at',
            'updated_at',
            'deleted_at',
        )

    def get_userprofile(self, article):
        data = UserProfileSerializer(article.writer.userprofile, context=self.context).data
        try:
            return data

        except ObjectDoesNotExist:
            return serializers.ValidationError("no such user")

    def get_need_type(self, article):
        data = NeedSerializer(article.need_type, context=self.context).data

        return data

    # def get_participant_count(self, article):
    #     article.

    # def get_current_price(self, article):
    #     data = article.order_chat.participant_profile.aggregate(Sum('price'))['price__sum']
    #     return data

    def create(self, validated_data):
        return Article.objects.create(**validated_data)


class NeedSerializer(serializers.ModelSerializer):
    people_min = serializers.IntegerField()
    price_min = serializers.IntegerField()

    class Meta:
        model = Article
        fields = (
            'people_min',
            'price_min',
        )
