from django.db import models

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    def create_user(self, email, nickname, date_joined, password=None):
        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
            date_joined=date_joined,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user


class Person(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name=_("Email address"),
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(
        verbose_name=_("Nickname"),
        max_length=30,
    )

    date_joined = models.DateTimeField(
        verbose_name=_("Date joined"), default=timezone.now
    )
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "nickname",
    ]

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_full_name(self):
        return self.nickname

    def get_short_name(self):
        return self.nickname
