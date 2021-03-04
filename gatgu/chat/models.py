from django.db import models
from django.contrib.auth.models import User
from article.models import Article
# Create your models here.

class OrderChat(models.Model):
    participants = models.ManyToManyField(
        User,
        through='ParticipantProfile',
        through_fields=('order_chat', 'participant'),
    )

    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name = 'order_chat'
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

    tracking_number = models.CharField(max_length=30)

    # following two attributes can be changed to price

class ChatMessage(models.Model):
    text = models.TextField(null=True)
    sent_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = 'messages'
    )
    sent_at = models.DateTimeField(auto_now=True)
    chat = models.ForeignKey(
        OrderChat,
        on_delete=models.CASCADE,
        related_name = 'messages'
    )
    media = models.URLField(null=True)
    type = models.CharField(max_length=30)

class ParticipantProfile(models.Model):
    order_chat = models.ForeignKey(
        OrderChat, 
        on_delete=models.CASCADE,
        related_name = 'participant_profile'
    )
    participant = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name = 'participant_profile'
    )
    joined_at = models.DateTimeField(auto_now=True)
    out_at = models.DateTimeField(null=True)
    pay_status = models.CharField(max_length=30)
    wish_price = models.IntegerField(null=True)

    class Meta:
        unique_together = (
            ('order_chat', 'participant')
        )
