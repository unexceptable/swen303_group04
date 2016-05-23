from django.contrib import admin
from .models import (
	Product, Category, Image, ChatHistory,
	Address, SalesOrder, OrderItem, WishList,
	WishListItem, Contact, Tag, Notification)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', '_thumb', 'description', 'category',
        'price', 'visible', 'added_on',)

class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('origin', 'to', 'message')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('subject', 'message_type', 'message', 'email', 'status')

class ImageAdmin(admin.ModelAdmin):
    list_display = ('_img', 'description')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'default', 'number_street','suburb', 'city','region', 'country', 'postcode')

class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'created_on',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'quantity', 'unit_price', 'product')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('to', 'notif', 'link')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_image', 'parent')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)
admin.site.register(Image, ImageAdmin)
admin.site.register(ChatHistory, ChatHistoryAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(WishList)
admin.site.register(WishListItem)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Notification, NotificationAdmin)
