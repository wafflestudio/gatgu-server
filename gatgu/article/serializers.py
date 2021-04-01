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
    location = serializers.CharField()

    need_type = serializers.ChoiceField(Article.NEED_TYPE, required=True)
    people_min = serializers.IntegerField(required=True)
    price_min = serializers.IntegerField(required=True)

    order_chat = serializers.SerializerMethodField()

    participants_summary = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'writer_id',
            'article_id',
            'title',
            'description',
            'location',
            'product_url',
            'thumbnail',
            'image',
            'need_type',
            'people_min',
            'price_min',
            'tag',
            'written_at',
            'updated_at',
            'deleted_at',

            'order_chat',

            'participants_summary',
        )

    def create(self, validated_data):
        article = super(ArticleSerializer, self).create(validated_data)
        OrderChat.objects.create(article=article)
        return article

    def get_order_chat(self, article):
        return OrderChatSerializer(article.order_chat).data

    def get_participants_summary(self, article):
        return ParticipantsSummarySerializer(article.order_chat.participant_profile).data


class ParticipantsSummarySerializer(serializers.Serializer):
    count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'count',
            'price'

        )

    def get_count(self, participants):
        return participants.count()

    def get_price(self, participants):
        return participants.aggregate(Sum('wish_price'))['wish_price__sum']


class SimpleArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    need_type = serializers.ChoiceField(Article.NEED_TYPE, required=True)
    people_min = serializers.IntegerField(required=True)
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
            'need_type',
            'people_min',
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


