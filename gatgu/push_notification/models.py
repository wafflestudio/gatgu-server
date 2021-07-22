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
    keyword = models.CharField(max_length=30, null=True)

    class Meta:
        unique_together = (
            ('user', 'token')
        )
