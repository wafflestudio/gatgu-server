from django.db.models import Sum
from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from chat.models import OrderChat, ParticipantProfile
from user.serializers import *

from article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    article_id = serializers.ReadOnlyField(source='id')
    deleted_at = serializers.DateTimeField(read_only=True)
    need_type = serializers.ChoiceField(Article.NEED_TYPE)
    people_min = serializers.IntegerField(required=True)
    price_min = serializers.IntegerField(required=True)

    order_status = serializers.IntegerField(write_only=True, required=False)
    tracking_number = serializers.IntegerField(write_only=True, required=False)

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
            'thumbnail_url',
            'need_type',
            'people_min',
            'price_min',
            'time_in',
            'written_at',
            'updated_at',
            'deleted_at',
            'order_status',
            'tracking_number',
            'participants_summary',
        )

    def create(self, validated_data):
        article = super(ArticleSerializer, self).create(validated_data)
        '''orderchat생성시 필요한 정보가 이게 끝인가'''
        OrderChat.objects.create(article=article)
        ParticipantProfile.objects.create(participant=article.writer, order_chat=article.order_chat)
        return article


    def create(self, validated_data):
        article = super(ArticleSerializer, self).create(validated_data)
        OrderChat.objects.create(article=article)
        ParticipantProfile.objects.create(participant=article.writer, order_chat=article.order_chat)
        return article

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
    participant_profile = serializers.SerializerMethodField

    class Meta:
        model = OrderChat
        fields = (
            'id',
            'order_status',
            'tracking_number',

            'participant_profile',

        )

    def get_participant_profile(self, orderchat):
        participants_profile = orderchat.participant_profile
        data = ParticipantProfileSerializer(participants_profile, many=True, context=self.context).data
        return data


class ParticipantProfileSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantProfile
        fields = (
            'id',
            'joined_at',
            'out_at',
            'pay_status',
            'wish_price',
            'participant_count',
        )

    def get_participant_count(self, orderchat):
        participant_count = orderchat.participant_profile.objects.all().count()
        return participant_count


class NeedSerializer(serializers.ModelSerializer):
    people_min = serializers.IntegerField()
    price_min = serializers.IntegerField()

    class Meta:
        model = Article
        fields = (
            'people_min',
            'price_min',
        )
