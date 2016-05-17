from django.contrib import admin
from .models import Product, Category, Image, ChatHistory, Address


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', '_thumb', 'description', 'category',
        'price', 'visible', 'added_on',)

class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('origin', 'to', 'message')

class ImageAdmin(admin.ModelAdmin):
    list_display = ('_img', 'description')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'number_street','suburb', 'city','region', 'country', 'postcode')


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Image, ImageAdmin)
admin.site.register(ChatHistory, ChatHistoryAdmin)
admin.site.register(Address, AddressAdmin)
