from django.db import models
from django.contrib.auth.models import User
from article.models import Article


# Create your models here.

class OrderChat(models.Model):
    participants = models.ManyToManyField(
        User,
        through='ParticipantProfile',
        through_fields=('chat', 'participant'),
    )
    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name='chat'
    )
    order_status = models.CharField(max_length=30)
    tracking_number = models.CharField(max_length=30)

    # following two attributes can be changed to price
    required_people = models.IntegerField()
    cur_people = models.IntegerField()


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


class ParticipantProfile(models.Model):
    chat = models.ForeignKey(
        OrderChat,
        on_delete=models.CASCADE,
    )
    participant = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    joined_at = models.DateTimeField(auto_now=True)
    out_at = models.DateTimeField(null=True)
    pay_status = models.CharField(max_length=30)
    wish_price = models.IntegerField(null=True)
