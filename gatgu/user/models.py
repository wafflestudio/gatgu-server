
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    picture = models.ImageField(default='default.jpg')
    nickname = models.CharField(max_length=10, db_index=True, blank=True, unique=True)
    address = models.CharField(max_length=20, blank=True) 
    phonenumber = models.CharField(max_length=13, db_index=True, blank=True, unique=True)
    withdrew_at = models.DateTimeField(null=True)

    USER_TYPE = (
        (1, 'django'),
        (2, 'kakao'),
        (3, 'google'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE, default=1, null=True)
    

