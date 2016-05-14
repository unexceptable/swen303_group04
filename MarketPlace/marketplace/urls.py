from django.conf.urls import include, url
from django.contrib import admin
from web_shop import urls as shop_urls
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^', include(shop_urls)),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
