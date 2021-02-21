from django.db import models
from django.contrib.auth.models import User
from article.models import Article
# Create your models here.

class OrderChat(models.Model):
    participants = models.ManyToManyField(
        User,
        through='ParticipantProfile',
        through_fields=('order_id', 'participant_id'),
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )
    order_status = models.CharField(max_length=30)
    tracking_number = models.CharField(max_length=30)
    required_people = models.IntegerField()
    cur_people = models.IntegerField()

class ChatMessages(models.Model):
    text = models.CharField(max_length=30)
    sent_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    sent_at = models.DateField()
    chatroom_id = models.ForeignKey(
        OrderChat,
        on_delete=models.CASCADE
    )
    media = models.CharField(max_length=1000)
    type = models.CharField(max_length=30)

class ParticipantProfile(models.Model):
    order_id = models.ForeignKey(
        OrderChat, 
        on_delete=models.CASCADE
    )
    participant_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    joined_at = models.DateField()
    out_at = models.DateField()
    pay_status = models.CharField(max_length=30)