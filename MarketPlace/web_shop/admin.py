from django.contrib import admin
from .models import Product, Category, Image, ChatHistory


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', '_thumb', 'description', 'category',
        'price', 'visible', 'added_on',)


class ImageAdmin(admin.ModelAdmin):
    list_display = ('_img', 'description')

class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('origin', 'to', 'message')


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Image, ImageAdmin)
admin.site.register(ChatHistory, ChatHistoryAdmin)
