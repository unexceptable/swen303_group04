from django.conf.urls import include, url
from django.contrib import admin
from web_shop import urls as shop_urls

urlpatterns = [
    url(r'^', include(shop_urls)),
    url(r'^admin/', include(admin.site.urls)),
]
