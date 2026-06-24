# dcrm/dcrm/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Configuración del panel de administración
admin.site.site_header = 'ANGELOW'
admin.site.site_title = 'Panel Admin'
admin.site.index_title = 'Bienvenido'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tienda.urls')),                     # Tienda - Página principal
    path('accounts/', include('website.urls')),           # Autenticación (login, register, logout)
    path('clientes/', include('clientes.urls')),          # CRM - Clientes
    
    # Google OAuth - Ruta correcta
    path('auth/', include('social_django.urls', namespace='social')),
]

# Archivos multimedia en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)