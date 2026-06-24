# dcrm/dcrm/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'ANGELOW'
admin.site.site_title = 'Panel Admin'
admin.site.index_title = 'Bienvenido'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tienda.urls')),
    path('accounts/', include('website.urls')),
    path('clientes/', include('clientes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)