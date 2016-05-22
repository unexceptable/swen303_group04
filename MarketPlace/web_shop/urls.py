"""colenso URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from .forms import CustomRegistrationForm
from registration.backends.simple.views import RegistrationView
from web_shop import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search[/]$', views.search, name='search'),
    url(r'^product/(?P<p_id>\w+)[/]$', views.product_detail),
    url(r'^product/(?P<p_id>\w+)/cart$', views.product_cart),
    url(r'^product/(?P<p_id>\w+)/wish$', views.product_wishlist),
    url(r'^category/(?P<category_name>\w+)[/]$', views.category_view),
    url(r'^login/$', views.signin),
    url(r'^logout/$', views.logout_user),
    url(r'^register/$', RegistrationView.as_view(form_class=CustomRegistrationForm), name='registrationr'),
    url(r'^editdetails/$', views.edit_details),
    url(r'^cart[/]$', views.cart_view),
    url(r'^cart/checkout[/]$', views.checkout),
    url(r'^cart/(?P<p_id>\w+)/update$', views.cart_update),
    url(r'^chat[/]$', views.chat, name='chat'),
    url(r'^chat-reload[/]$', views.chat_reload, name='chat-reload'),
    url(r'^listusers/$', views.listusers),
    url(r'^listsales/$', views.listsales),
    url(r'^sales-details/(?P<s_id>\w+)[/]$', views.sales_details),
    url(r'^contact/$', views.contact),
    url(r'^listcontacts/$', views.listcontacts),
    url(r'^wishlist[/]$', views.wishlist),
    url(r'^wishlist/(?P<p_id>\w+)[/]$', views.wishlist_update),
    url(r'^wishlist/(?P<p_id>\w+)/cart[/]$', views.wishlist_cart),
    url(r'^listaddresses/$', views.listaddresses),
    url(r'^editaddress/(?P<uid>\w+)[/]$', views.edit_address),
    url(r'^defaultaddress/(?P<uid>\w+)[/]$', views.default_address),
    url(r'^addaddress/$', views.add_address),
    url(r'^notifications/$', views.listnotifications),
]
