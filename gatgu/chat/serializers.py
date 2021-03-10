from django.db.models import Sum
from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from chat.models import OrderChat, ParticipantProfile, ChatMessage
from user.serializers import *


class OrderChatSerializer(serializers.ModelSerializer):
    participant_profile = serializers.SerializerMethodField()

    class Meta:
        model = OrderChat
        fields = (
            'id',
            'order_status',
            'tracking_number',
            'participant_profile',
        )

    def get_participant_profile(self, orderchat):
        print(orderchat)
        participants_profile = orderchat.participant_profile
        data = ParticipantProfileSerializer(participants_profile, many=True, context=self.context).data
        return data


class ParticipantProfileSerializer(serializers.ModelSerializer):
    #participant_count = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantProfile
        fields = (
            'id',
            'joined_at',
            'out_at',
            'pay_status',
            'wish_price',
        )

'''    def get_participant_count(self, participant_profile):
        print(participant_profile)
        participant_count = participant_profile.objects.all().count()
        print(participant_count)
        return participant_count'''

class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'text',
            'media',
            'sent_by_id',
            'sent_at'
        )
