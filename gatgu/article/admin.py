from django.contrib import admin

from article.models import Article
from chat import models
from chat.models import ChatMessage


class OrderChatInline(admin.TabularInline):
    model = models.OrderChat


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ordering = ['written_at']
    # search_fields = ['writer', 'title']

    list_display = ['writer', 'title', 'description', 'written_at', 'updated_at', 'deleted_at']
    list_display_links = ['writer', 'title']
    list_per_page = 10
    list_filter = ['writer', 'tag']

    inlines = (OrderChatInline,)


@admin.register(ChatMessage)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['text', 'sent_by', 'sent_at']
    list_display_links = ['text']
    list_filter = ['chat', 'sent_by']
    list_per_page = 15
