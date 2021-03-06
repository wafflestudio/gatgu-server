from django.contrib import admin
from django.utils.safestring import mark_safe
from . import models


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'username',
        'picture',
        'nickname',
        'updated_at',
        'withdrew_at'
    )
    list_display_links = (
        'user_id',
        'picture',
    )

    list_filter = (
        'user_id',
        'updated_at',
        'withdrew_at',
    )


    def username(self, userprofile):
        return mark_safe('{}'.format(userprofile.user.username))
    username.short_description = '아이디'
