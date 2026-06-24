# website/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Usuario, PerfilUsuario, Record, ActividadUsuario

# ============================================================
# ADMIN DE USUARIO PERSONALIZADO
# ============================================================

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'rol', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['rol', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'telefono', 'direccion', 'fecha_nacimiento')
        }),
        ('Seguridad', {
            'fields': ('intentos_fallidos', 'bloqueado_hasta'),
            'classes': ('collapse',)
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'telefono', 'direccion', 'fecha_nacimiento')
        }),
    )


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_actualizacion']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['fecha_actualizacion']


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    # CORREGIDO: 'phone_number' -> 'phone' (el campo en el modelo es 'phone')
    list_display = [
        'id', 
        'first_name', 
        'last_name', 
        'email', 
        'phone',        # <--- CAMBIADO: era 'phone_number'
        'city', 
        'state', 
        'created_at'
    ]
    list_filter = ['city', 'state', 'created_at', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Dirección', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Auditoría', {
            'fields': ('usuario', 'updated_by', 'is_active', 'notas'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActividadUsuario)
class ActividadUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'descripcion', 'fecha']
    list_filter = ['tipo', 'fecha']
    search_fields = ['usuario__username', 'descripcion']
    readonly_fields = ['fecha']
    list_per_page = 50