from django.contrib.auth.models import User
from django.db import models


class DeviceToken(models.Model):
    token = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_token')
    created_at = models.DateTimeField(auto_now_add=True)

