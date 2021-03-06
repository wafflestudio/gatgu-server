from django.contrib import admin
from django.utils.safestring import mark_safe
from . import models


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'writer_id',
        'title',
        'thumbnail_url',
        'written_at',
        'updated_at',
        'deleted_at',
    )
    list_display_links = (
        'title',
    )
    list_filter = (
        'writer_id', 
        'written_at',
        'updated_at',
        'deleted_at',
    )