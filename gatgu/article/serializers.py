from django.db.models import Sum
from chat.models import OrderChat
from chat.serializers import OrderChatSerializer
from user.serializers import *

from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    deleted_at = serializers.DateTimeField(read_only=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    trading_place = serializers.CharField(required=True)
    product_url = serializers.URLField(required=True)

    price_min = serializers.IntegerField(required=True)
    article_status = serializers.SerializerMethodField()
    order_chat = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'description',
            'trading_place',
            'product_url',
            'article_status',
            'image',
            'price_min',
            'tag',
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


class ParticipantsSummarySerializer(serializers.Serializer):
    count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'count',
            'price',
        )

    def get_count(self, order_chat):
        return order_chat.count_participant

    def get_price(self, order_chat):
        return order_chat.sum_wish_price


class SimpleArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    price_min = serializers.IntegerField(required=True)
    article_status = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'trading_place',
            'image',
            'price_min',
            'tag',
            'time_in',
            'article_status',
            'updated_at',
        )

    def get_article_status(self, article):
        data = ParticipantsSummarySerializer(article.order_chat).data
        data['progress_status'] = article.article_status
        return data
