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

    '''participant info'''

    participants = serializers.SerializerMethodField()
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

            'participants',
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

    def get_participants(self, article):
        # data = OrderChatSerializer(article.chat, context=self.context).data
        # participant_profile = article.id.participant_profile.objects.all()

        '''OrderChat 객체가 생성되기 전이라 article.order_chat을 찾을 수 없나?
        article create 시 chat 생성하도록 위에 추가 시킨 후 OrderChat에 pay_status가 없다는 오류 발생'''

        participant_profile = article.order_chat
        data = ParticipantProfileSerializer(participant_profile, context=self.context).data

        return data


class OrderChatSerializer(serializers.ModelSerializer):
    participant_profile = serializers.SerializerMethodField

    class Meta:
        model = OrderChat
        fields = (
            'id',
            'participant_profile',
            'order_status',
            'tracking_number',
        )

    def get_participant_profile(self, orderchat):
        participants_profile = orderchat.participant_profile.objects.all()
        return ParticipantProfileSerializer(participants_profile, many=True).data

    # def get_current_price_sum(self, article):
    #     price_sum = article.chat.participant_profile.aggregate(Sum('price'))['price__sum']
    #     return price_sum


class ParticipantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantProfile
        fields = (
            '__all__'
        )


# def create(self, validated_data):
#     validated_data.pop('participant_count', '')
#     validated_data.pop('current_price_sum', '')
#
#     return Article.objects.create(**validated_data)


class NeedSerializer(serializers.ModelSerializer):
    people_min = serializers.IntegerField()
    price_min = serializers.IntegerField()

    class Meta:
        model = Article
        fields = (
            'people_min',
            'price_min',
        )
