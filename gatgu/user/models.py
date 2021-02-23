from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, related_name='userprofile', on_delete=models.CASCADE)
    picture = models.ImageField(default='default.jpg')
    nickname = models.CharField(
        max_length=20, db_index=True)
    phone = models.CharField(
        max_length=13, db_index=True, unique=True)
    is_snu = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    withdrew_at = models.DateTimeField(null=True)
