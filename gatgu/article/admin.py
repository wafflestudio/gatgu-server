from django.contrib import admin

from article.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['writer', 'title', 'description', 'written_at', 'updated_at', 'deleted_at']
    list_display_links = ['writer', 'title']
