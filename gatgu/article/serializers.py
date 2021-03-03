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

    '''Chat info'''
    order_chat = serializers.SerializerMethodField()
    order_status = serializers.IntegerField(write_only=True, required=False)
    tracking_number = serializers.IntegerField(write_only=True, required=False)

    '''participant info'''

    # participants = serializers.SerializerMethodField()
    # joined_at = serializers.DateTimeField(read_only=True)
    # out_at = serializers.DateTimeField(read_only=True)
    # pay_status = serializers.BooleanField(read_only=True)
    # wish_price = serializers.IntegerField(read_only=True)

    # participant_id = serializers.SerializerMethodField
    # participant_count = serializers.SerializerMethodField

    # current_price_sum = serializers.SerializerMethodField

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

            'order_chat',
            'order_status',
            'tracking_number',

            # 'participant_count',

            # 'current_price_sum',
        )

    def create(self, validated_data):
        article = super(ArticleSerializer, self).create(validated_data)
        '''orderchat생성시 필요한 정보가 이게 끝인가'''
        OrderChat.objects.create(article=article)

        return article

    # def get_userprofile(self, article):
    #     data = UserProfileSerializer(article.writer.userprofile, context=self.context).data
    #     try:
    #         return data
    #
    #     except ObjectDoesNotExist:
    #         return serializers.ValidationError("no such user")

    # def get_need_type(self, article):
    #     data = NeedSerializer(article.need_type, context=self.context).data
    #
    #     return data

    def create(self, validated_data):
        article = super(ArticleSerializer, self).create(validated_data)
        OrderChat.objects.create(article=article)

        return article

    def get_order_chat(self, article):
        order_chat = article.order_chat
        data = OrderChatSerializer(order_chat, context=self.context).data
        return data

    def get_participants(self, article):
        # data = OrderChatSerializer(article.chat, context=self.context).data
        # participant_profile = article.order_chat.participant_profile
        participant_profile = article.order_chat.participant_profile
        data = ParticipantProfileSerializer(participant_profile, many=True, context=self.context).data
        return data


class OrderChatSerializer(serializers.ModelSerializer):
    participant_profile = serializers.SerializerMethodField
    # participants_count = serializers.SerializerMethodField
    joined_at = serializers.DateTimeField(read_only=True)
    out_at = serializers.DateTimeField(read_only=True)
    pay_status = serializers.BooleanField(read_only=True)
    wish_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderChat
        fields = (
            'id',
            'order_status',
            'tracking_number',

            'participant_profile',
            # 'participant_count',
            'joined_at',
            'out_at',
            'pay_status',
            'wish_price',

        )

    def get_participant_profile(self, orderchat):
        participants_profile = orderchat.participant_profile
        data = ParticipantProfileSerializer(participants_profile, many=True, context=self.context).data
        return data

    # def get_participant_count(self, orderchat):
    #     participant_count = orderchat.participant_profile.objects.all().count()
    #     return participant_count







    # def get_current_price_sum(self, article):
    #     price_sum = article.chat.participant_profile.aggregate(Sum('price'))['price__sum']
    #     return price_sum


class ParticipantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantProfile
        fields = (
            '__all__'
        )


class NeedSerializer(serializers.ModelSerializer):
    people_min = serializers.IntegerField()
    price_min = serializers.IntegerField()

    class Meta:
        model = Article
        fields = (
            'people_min',
            'price_min',
        )
