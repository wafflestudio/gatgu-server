from django.db import models
from django.contrib.auth.models import User
from article.models import Article


class OrderChat(models.Model):
    # ORDER_STATUS = (
    #     (1, 'WAITING_MEMBERS'),
    #     (2, 'WAITING_PAY'),
    #     (3, 'WAITING_PARCELS'),
    #     (4, 'GATGU_COMPLETE'),
    # )

    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='order_chat')
    # order_status = models.PositiveSmallIntegerField(choices=ORDER_STATUS, default=1, null=True)
    tracking_number = models.CharField(max_length=30, null=True)


class ChatMessage(models.Model):
    text = models.TextField(null=True)
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    sent_at = models.DateTimeField(auto_now=True)
    chat = models.ForeignKey(OrderChat, on_delete=models.CASCADE, related_name='messages')
    type = models.CharField(max_length=30)

class ChatMessageImage(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='image')
    img_url = models.URLField(blank=True)

# order_chat 과 user(participant)의 관계 테이블
class ParticipantProfile(models.Model):
    PAY_STATUS = (
        (1, '입금 전 '),
        (2, '입금 확인요청'),
        (3, '입금 완료'),
    )
    order_chat = models.ForeignKey(OrderChat, on_delete=models.CASCADE, related_name='participant_profile')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participant_profile')
    pay_status = models.IntegerField(choices=PAY_STATUS, default=1)
    wish_price = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('order_chat', 'participant')
        )
