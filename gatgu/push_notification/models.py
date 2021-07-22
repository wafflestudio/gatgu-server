from django.contrib.auth.models import User
from django.db import models


class FCMToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    fcmtoken = models.CharField(max_length=300)


class UserFCMToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_fcmtoken')
    token = models.ForeignKey(FCMToken, on_delete=models.CASCADE, related_name='user_fcmtoken')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('user', 'token')
        )


class KeyWord(models.Model):
    keyword = models.CharField(max_length=30)


class UserKeyWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.ForeignKey(KeyWord, on_delete=models.CASCADE, related_name='keyowrds')

    class Meta:
        unique_together = (
            ('user', 'keyword')
        )
