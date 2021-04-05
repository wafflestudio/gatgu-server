from django.db import models
from django.contrib.auth.models import User
from article.models import Article


class OrderChat(models.Model):
    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name='order_chat'
    )

    participants = models.ManyToManyField(
        User,
        related_name = 'order_chat',
        through = 'ParticipantProfile'
    )

    ORDER_STATUS = (
        (1, 'WAITING_MEMBERS'),
        (2, 'MEMBER_ASSEMBLED'),
        (3, 'PAY_STATUS_CHECKED'),
        (4, 'ORDER_COMPLETE'),
        (5, 'WAITING_PARCELS'),
        (6, 'WAITING_SHARE'),
        (7, 'GATGU_COMPLETE'),
    )

    order_status = models.PositiveSmallIntegerField(choices=ORDER_STATUS, default=1, null=True)

    tracking_number = models.CharField(max_length=30, null=True)


class ChatMessage(models.Model):
    text = models.TextField(null=True)
    sent_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages'

    )
    sent_at = models.DateTimeField(auto_now=True)
    chat = models.ForeignKey(
        OrderChat,
        on_delete=models.CASCADE,

        related_name='messages'

    )
    media = models.URLField(null=True)
    type = models.CharField(max_length=30)
    system = models.BooleanField(defalut=False)


class ParticipantProfile(models.Model):
    order_chat = models.ForeignKey(
        OrderChat,
        on_delete=models.CASCADE,
        related_name='participant_profile',
    )
    participant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='participant_profile',
    )
    joined_at = models.DateTimeField(auto_now=True)
    pay_status = models.BooleanField(default=False)
    wish_price = models.IntegerField(null=True)

    class Meta:
        unique_together = (
            ('order_chat', 'participant')
        )
