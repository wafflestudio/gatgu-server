<<<<<<< HEAD
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    area = models.CharField(max_length=20, blank=True)
    nickname = models.CharField(max_length=10, db_index=True, blank=True, unique=True)
    phone = models.CharField(max_length=13, db_index=True, blank=True, unique=True)
    USER_TYPE = (
        (1, 'django'),
        (2, 'kakao'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE, default=1, null=True)
    profile_pics = models.ImageField(default='default.jpg')
||||||| 78d8143
=======
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, related_name='userprofile', on_delete=models.CASCADE)
    picture = models.ImageField(default='default.jpg')
    nickname = models.CharField(
        max_length=10, db_index=True, blank=True, unique=True)
    address = models.CharField(max_length=20, blank=True)
    phone = models.CharField(
        max_length=13, db_index=True, blank=True, unique=True)
    is_snu = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    withdrew_at = models.DateTimeField(null=True)
>>>>>>> 9a699bd6ac283118129a8de9d6ba65fc1b3cc756
