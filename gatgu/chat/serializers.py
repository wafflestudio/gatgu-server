from chat.models import OrderChat, ParticipantProfile, ChatMessage, ChatMessageImage
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
            'recent_message'
        )

    def get_recent_message(self, orderchat):
        message = orderchat.messages.last()
        data = ChatMessageSerializer(message, context=self.context).data
        return data


class ParticipantProfileSerializer(serializers.ModelSerializer):
    participant = serializers.SerializerMethodField()

    class Meta:
        model = ParticipantProfile
        fields = (
            'id',
            'pay_status',
            'wish_price',
            'participant',
            'joined_at',
        )

    def get_participant(self, participant_profile):
        user_profile = participant_profile.participant.userprofile

        data = SimpleParticipantsSerializer(user_profile, context=self.context).data
        return data

class ChatMessageSerializer(serializers.ModelSerializer):
    sent_by = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'text',
            'image',
            'sent_by',
            'sent_at',
            'type'
        )

    def get_sent_by(self, chatmessage):
        sent_by = chatmessage.sent_by.userprofile
        data = UserProfileSerializer(sent_by, context=self.context).data
        return data
    
    def get_image(self, chatmessage):
        image = chatmessage.image.all()
        return ChatMessageImageSerializer(image, many=True).data

class ChatMessageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageImage
        fields = (
            'id',
            'img_url'
        )