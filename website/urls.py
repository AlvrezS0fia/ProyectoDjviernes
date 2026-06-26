# website/urls.py

from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    # ===== PÁGINAS PRINCIPALES =====
    path('', views.home, name='home'),
    
    # ===== AUTENTICACIÓN =====
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # ===== DASHBOARDS =====
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/user/', views.dashboard_user, name='dashboard_user'),
    
    # ===== USUARIO =====
    path('favoritos/', views.favorites_view, name='favorites'),
    path('perfil/', views.perfil_view, name='perfil'),
    
    # ===== ADMIN - AUDITORÍA =====
    path('actividades/', views.actividades_view, name='actividades'),
    
    # ===== GESTIÓN CLIENTES (Admin) =====
    path('gestion-clientes/', views.gestion_clientes, name='gestion_clientes'),
    path('gestion-clientes/nuevo/', views.cliente_crear, name='cliente_crear'),
    path('gestion-clientes/editar/<int:cliente_id>/', views.cliente_editar, name='cliente_editar'),
    path('gestion-clientes/eliminar/<int:cliente_id>/', views.cliente_eliminar, name='cliente_eliminar'),
    path('gestion-clientes/detalle/<int:cliente_id>/', views.cliente_detalle, name='cliente_detalle'),
    path('gestion-clientes/activar/<int:cliente_id>/', views.cliente_activar, name='cliente_activar'),
    
    # ===== API - FAVORITOS =====
    path('api/favoritos/', views.api_favoritos, name='api_favoritos'),
    path('api/favoritos/toggle/', views.api_toggle_favorito, name='api_toggle_favorito'),
    
    # ===== API - SESIÓN =====
    path('api/session-status/', views.session_status, name='session_status'),
]