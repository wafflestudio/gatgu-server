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
        participants_profile = orderchat.participant_profile
        data = ParticipantProfileSerializer(participants_profile, many=True, context=self.context).data
        return data


class SimpleOrderChatSerializer(serializers.ModelSerializer):
    recent_message = serializers.SerializerMethodField()

    class Meta:
        model = OrderChat
        fields = (
            'id',
            'order_status',
            'tracking_number',
            #'participant_profile',
            'recent_message'
        )
    
    def get_recent_message(self, orderchat):
        message = orderchat.messages.last()
        data = ChatMessageSerializer(message, context=self.context).data
        return data

class ParticipantProfileSerializer(serializers.ModelSerializer):
    #participant_count = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantProfile
        fields = (
            'id',
            'joined_at',
            'pay_status',
            'wish_price',
            'participant'
        )
    
    def get_participant(self, participant_profile):
        user_profile = participant_profile.participant.userprofile
        data = UserProfileSerializer(user_profile, context=self.context).data
        return data

'''    def get_participant_count(self, participant_profile):
        print(participant_profile)
        participant_count = participant_profile.objects.all().count()
        print(participant_count)
        return participant_count'''

class ChatMessageSerializer(serializers.ModelSerializer):
    sent_by = serializers.SerializerMethodField()
    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'text',
            'media',
            'system',
            'sent_by',
            'sent_at'
        )

    def get_sent_by(self, chatmessage):
        sent_by = chatmessage.sent_by.userprofile
        data = UserProfileSerializer(sent_by, context=self.context).data
        return data    
    
