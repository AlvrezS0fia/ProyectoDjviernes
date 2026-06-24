# clientes/urls.py

from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # CRUD Principal
    path('', views.cliente_list, name='cliente_list'),
    path('nuevo/', views.cliente_create, name='cliente_create'),
    path('editar/<int:pk>/', views.cliente_update, name='cliente_update'),
    path('eliminar/<int:pk>/', views.cliente_delete, name='cliente_delete'),
    path('detalle/<int:pk>/', views.cliente_detail, name='cliente_detail'),
    
    # Funcionalidades adicionales
    path('exportar/', views.cliente_export, name='cliente_export'),
    path('importar/', views.cliente_import, name='cliente_import'),
    
    # API
    path('api/', views.cliente_api, name='cliente_api'),
]