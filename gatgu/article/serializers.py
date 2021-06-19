import datetime
from django.db.models import Sum, Subquery, OuterRef, Count, IntegerField, Prefetch
from django.db.models.functions import Coalesce

from chat.models import OrderChat, ParticipantProfile
from chat.serializers import OrderChatSerializer
from user.serializers import *

from article.models import Article, ArticleTag, Tag, ArticleImage


class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    deleted_at = serializers.DateTimeField(read_only=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    trading_place = serializers.CharField(required=True)
    product_url = serializers.CharField(required=True, max_length=200)
    time_in = serializers.DateField(default=datetime.date.today() + datetime.timedelta(days=7))

    price_min = serializers.IntegerField(required=True)
    article_status = serializers.SerializerMethodField()
    order_chat = serializers.SerializerMethodField()

    image = serializers.SerializerMethodField(required=False)
    tag = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'description',
            'image',
            'tag',
            'trading_place',
            'product_url',
            'time_in',
            'price_min',

            'article_status',
            'order_chat',
            'written_at',
            'updated_at',
            'deleted_at',

        )

    def create(self, validated_data):
        article = super(ArticleSerializer, self).create(validated_data)
        OrderChat.objects.create(article=article)
        return article

    def get_order_chat(self, article):
        return OrderChatSerializer(article.order_chat).data

    def get_article_status(self, article):
        data = ParticipantsSummarySerializer(article.order_chat).data
        data['progress_status'] = article.article_status
        return data

    def get_image(self, article):
        return ArticleImageSerializer(article.images, many=True).data

    def get_tag(self, article):
        return TagSerializer(article.tags, many=True).data


class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = (
            'id',
            'img_url',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'name',
        )


class ParticipantsSummarySerializer(serializers.Serializer):
    cur_price_sum = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'cur_people_sum',
            'cur_price_sum',
        )

    def get_cur_people_sum(self, order_chat):
        return order_chat.count_participant

    def get_cur_price_sum(self, order_chat):
        return order_chat.sum_wish_price


class SimpleArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    price_min = serializers.IntegerField(default=0)
    article_status = serializers.SerializerMethodField()

    image = serializers.SerializerMethodField(required=False)
    # tag = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'trading_place',
            'image',
            # 'tag',
            'price_min',
            'time_in',
            'article_status',
            'updated_at',
        )

    def get_article_status(self, article):
        data = ParticipantsSummarySerializer(article.order_chat).data
        data['progress_status'] = article.article_status
        return data

    def get_image(self, article):
        #image하나만 받아올 것
        return ArticleImageSerializer(article.images, many=True).data

    # def get_tag(self, article):
    #     return ArticleTagSerializer(article.tags, many=True).data
