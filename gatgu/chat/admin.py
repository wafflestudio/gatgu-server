from django.contrib import admin

from chat.models import OrderChat


@admin.register(OrderChat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['article', 'order_status', 'tracking_number']
    list_display_links = ['article']
