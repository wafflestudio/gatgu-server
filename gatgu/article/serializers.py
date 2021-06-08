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

            'article_status',

            'description',
            'trading_place',
            'product_url',
            'image',
            'price_min',
            'tag',
            'written_at',
            'updated_at',
            'deleted_at',

            'order_chat',

        )

    def create(self, validated_data):
        article = super(ArticleSerializer, self).create(validated_data)
        OrderChat.objects.create(article=article)
        return article

    def get_order_chat(self, article):
        return OrderChatSerializer(article.order_chat).data

    def get_article_status(self, article):
        data = ParticipantsSummarySerializer(article.order_chat.participant_profile).data
        data['progress_status'] = article.article_status
        return data


class ParticipantsSummarySerializer(serializers.Serializer):
    count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'count',
            'price',
            'progress_status',
        )

    def get_count(self, participants):
        return participants.count()

    # 글 작성자를 제외한 참가자들의 희망 금액의 총합
    def get_price(self, participants):
        return participants.aggregate(Sum('wish_price'))['wish_price__sum']


class SimpleArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    price_min = serializers.IntegerField(required=True)

    participants_summary = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'location',
            'thumbnail',
            'price_min',
            'tag',
            'written_at',
            'updated_at',

            'participants_summary',
            'order_status',

        )

    def get_participants_summary(self, article):
        return ParticipantsSummarySerializer(article.order_chat.participant_profile).data

    def get_order_status(self, article):
        return article.order_chat.order_status
