from django.db.models import Sum
from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from chat.models import OrderChat, ParticipantProfile
from user.serializers import *

from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    deleted_at = serializers.DateTimeField(read_only=True)
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
            'need_type',
            'people_min',
            'price_min',
            # 'time_in',
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


class OrderChatSerializer(serializers.ModelSerializer):
    participants_profile = serializers.SerializerMethodField()

    class Meta:
        model = OrderChat
        fields = (
            'id',
            'order_status',
            'tracking_number',

            'participants_profile',

        )

    def get_participants_profile(self, orderchat):
        participants_profile = orderchat.participant_profile
        data = ParticipantProfileSerializer(participants_profile, many=True, context=self.context).data
        return data


class ParticipantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantProfile
        fields = (
            'id',
            'joined_at',
            'pay_status',
            'wish_price',
        )


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
            'written_at',
            'updated_at',

            'participants_summary',
            'order_status',

        )

    def get_participants_summary(self, article):
        return ParticipantsSummarySerializer(article.order_chat.participant_profile).data

    def get_order_status(self, article):
        return article.order_chat.order_status
