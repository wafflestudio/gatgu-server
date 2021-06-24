from django.contrib.auth.models import User
from django.db import models


# def profile_avatar_path(instance, filename):
#     return 'accounts/avatar/{}/{}'.format(instance.user.username, filename)


class UserProfile(models.Model):
    GRADE = (
        (1, '같구초보'),
        (2, '같구중수'),
        (3, '같구고수'),
        (4, '같구마스터'),

    )

    user = models.OneToOneField(
        User, related_name='userprofile', on_delete=models.CASCADE)
    picture = models.TextField(null=True)
    nickname = models.CharField(
        max_length=20, db_index=True, null=False)
    updated_at = models.DateTimeField(auto_now=True)
    withdrew_at = models.DateTimeField(null=True)
    point = models.IntegerField(default=0, null=True)
    grade = models.PositiveSmallIntegerField(choices=GRADE, default=1, null=True)
    trading_address = models.CharField(max_length=50, null=True)
