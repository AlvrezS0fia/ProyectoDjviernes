# website/urls.py

from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    # Autenticación
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/user/', views.dashboard_user, name='dashboard_user'),
    
    # Usuario
    path('favoritos/', views.favorites_view, name='favorites'),
    path('perfil/', views.perfil_view, name='perfil'),
    
    # Admin - Auditoría
    path('actividades/', views.actividades_view, name='actividades'),
    
    # API
    path('api/session-status/', views.session_status, name='session_status'),
]