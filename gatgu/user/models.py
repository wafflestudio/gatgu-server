from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, related_name='userprofile', on_delete=models.CASCADE)
    picture = models.ImageField(default='default.jpg')
    nickname = models.CharField
        max_length=20, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    withdrew_at = models.DateTimeField(null=True)


class EmailProfile(models.Model):

    email = models.EmailField()
    is_certificated = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    code = models.CharField(max_length=10)
