from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from user.serializers import *

from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    deleted_at = serializers.DateTimeField(read_only=True)
    time_remaining = serializers.DateTimeField(read_only=True)
    # need_type = serializers.SerializerMethodField()
    # people_min = serializers.IntegerField(write_only=True)
    # price_min = serializers.IntegerField(write_only=True)
    is_deleted = serializers.BooleanField(read_only=True)

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
            # 'need_type',
            'people_min',
            'price_min',
            'time_max',
            'time_remaining',
            'created_at',
            'updated_at',
            'deleted_at',
            'is_deleted',

        )

    def get_userprofile(self, article):
        data = UserProfileSerializer(article.writer.userprofile, context=self.context).data
        try:
            return data

        except ObjectDoesNotExist:
            return serializers.ValidationError("no such user")

    def get_need_type(self, article):
        data = NeedSerializer(article.need_type, context=self.context).data

        # data = NeedPeopleSerializer(article.need_type,
        #                             context=self.context).data if article.need_type == 1 else NeedPriceSerializer(
        #     article.need_type, context=self.context).data

        return data

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

# class NeedPeopleSerializer(serializers.ModelSerializer):
#     people_min = serializers.IntegerField()
#
#     class Meta:
#         model = Article
#         fields = (
#             'people_min',
#         )
#
#
# class NeedPriceSerializer(serializers.ModelSerializer):
#     price_min = serializers.IntegerField()
#
#     class Meta:
#         model = Article
#         fields = (
#             'price_min',
#         )
