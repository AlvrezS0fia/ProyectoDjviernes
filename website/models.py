# website/models.py

"""
Modelos de la aplicación website para ANGELOW
Define el modelo de Usuario personalizado, perfiles y registros
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import re
from datetime import timedelta
from django.utils import timezone

# ============================================================
# 1. VALIDADORES PERSONALIZADOS (Expresiones Regulares - Capa 3)
# ============================================================

def validate_username(value):
    """
    Valida nombre de usuario con expresión regular
    Solo permite: letras, números, guiones bajos y puntos
    Longitud: 4-20 caracteres
    """
    if not re.match(r'^[a-zA-Z0-9_.]{4,20}$', value):
        raise ValidationError(
            'El nombre de usuario debe tener entre 4 y 20 caracteres y '
            'solo puede contener letras, números, guiones bajos y puntos.'
        )
    return value

def validate_no_special_chars(value):
    """
    Valida que no contenga caracteres especiales peligrosos
    Permite: letras, números, espacios, guiones, puntos y acentos
    """
    if not re.match(r'^[a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ.]+$', value):
        raise ValidationError(
            'Este campo solo puede contener letras, números, espacios, '
            'guiones y puntos.'
        )
    return value

def validate_phone_number(value):
    """
    Valida número de teléfono con expresión regular
    Permite: +, números, espacios y guiones
    """
    if not re.match(r'^\+?[\d\s-]{7,20}$', value):
        raise ValidationError(
            'Ingresa un número de teléfono válido (mínimo 7 dígitos).'
        )
    return value

def validate_zip_code(value):
    """
    Valida código postal (solo números, 5-10 dígitos)
    """
    if not re.match(r'^\d{5,10}$', value):
        raise ValidationError(
            'El código postal debe contener solo números (5-10 dígitos).'
        )
    return value

def validate_email(value):
    """
    Valida formato de email con expresión regular
    """
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        raise ValidationError(
            'Ingresa un correo electrónico válido (ejemplo: usuario@dominio.com).'
        )
    return value

# ============================================================
# 2. MODELO DE USUARIO PERSONALIZADO (Single Responsibility - SRP)
# ============================================================

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    Añade roles y campos adicionales para ANGELOW
    
    Principios aplicados:
    - SRP: Solo maneja la autenticación y roles de usuario
    - DRY: Hereda de AbstractUser, no reescribimos lo que ya existe
    - LSP: Puede ser usado donde se espera un User de Django
    """
    
    # ============================================================
    # ROLES DEL SISTEMA (Autorización - Capa 2)
    # ============================================================
    ROLES = (
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('user', 'Usuario Regular'),
    )
    
    # ============================================================
    # CAMPOS DEL MODELO
    # ============================================================
    rol = models.CharField(
        max_length=10, 
        choices=ROLES, 
        default='user',
        help_text='Rol del usuario en el sistema'
    )
    
    # Campos adicionales para el perfil
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number]
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        help_text='Dirección de residencia o envío'
    )
    
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de nacimiento del usuario'
    )
    
    # Campos de auditoría (Capa 4 - Seguridad)
    ultimo_cambio_password = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Última vez que se cambió la contraseña'
    )
    
    intentos_fallidos = models.PositiveIntegerField(
        default=0,
        help_text='Número de intentos de login fallidos'
    )
    
    bloqueado_hasta = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Fecha hasta que el usuario está bloqueado'
    )

    # ============================================================
    # MÉTODOS DEL MODELO
    # ============================================================
    
    def __str__(self):
        """Representación legible del usuario"""
        return f"{self.get_full_name() or self.username} (@{self.username})"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario (DRY)"""
        return self.get_full_name() or self.username
    
    def es_administrador(self):
        """Verifica si el usuario es administrador"""
        return self.rol == 'admin'
    
    def es_vendedor(self):
        """Verifica si el usuario es vendedor"""
        return self.rol == 'vendedor'
    
    def es_usuario_regular(self):
        """Verifica si el usuario es regular"""
        return self.rol == 'user'
    
    def tiene_permiso(self, permiso_requerido):
        """
        Verifica si el usuario tiene un permiso específico
        Implementación flexible para futuros permisos
        """
        permisos_por_rol = {
            'admin': ['ver_todo', 'editar_todo', 'eliminar_todo', 'acceso_crm', 'acceso_tienda', 'ver_reportes'],
            'vendedor': ['ver_clientes', 'editar_clientes', 'acceso_crm', 'ver_productos'],
            'user': ['ver_productos', 'comprar', 'acceso_tienda', 'ver_perfil'],
        }
        return permiso_requerido in permisos_por_rol.get(self.rol, [])
    
    def incrementar_intentos_fallidos(self):
        """Incrementa el contador de intentos fallidos (Seguridad)"""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
        self.save()
    
    def resetear_intentos(self):
        """Resetea los intentos fallidos después de un login exitoso"""
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save()
    
    def esta_bloqueado(self):
        """Verifica si el usuario está temporalmente bloqueado"""
        if self.bloqueado_hasta:
            return timezone.now() < self.bloqueado_hasta
        return False
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['rol']),
        ]


# ============================================================
# 3. MODELO DE PERFIL DE USUARIO (Extensión - SRP)
# ============================================================

class PerfilUsuario(models.Model):
    """
    Modelo para almacenar información adicional del perfil
    Separado del modelo Usuario para mantener SRP
    """
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil',
        help_text='Usuario asociado a este perfil'
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Biografía o descripción del usuario'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text='Foto de perfil del usuario'
    )
    
    preferencias = models.JSONField(
        default=dict,
        blank=True,
        help_text='Preferencias del usuario (JSON)'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización del perfil'
    )
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'


# ============================================================
# 4. MODELO RECORD (TU MODELO ORIGINAL MEJORADO)
# ============================================================

class Record(models.Model):
    """
    Modelo para el registro de clientes (CRM)
    Tu modelo original mejorado con validaciones y auditoría
    
    Principios aplicados:
    - SRP: Maneja solo información de clientes
    - DRY: Reutiliza validadores personalizados
    - Seguridad: Validaciones con regex (Capa 3)
    """
    
    # ============================================================
    # RELACIONES
    # ============================================================
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='records',
        null=True,
        blank=True,
        help_text='Usuario que creó o gestiona este registro'
    )
    
    # ============================================================
    # CAMPOS PRINCIPALES (TU ESTRUCTURA ORIGINAL)
    # ============================================================
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación del registro'
    )
    
    first_name = models.CharField(
        max_length=50,
        validators=[validate_no_special_chars],
        help_text='Nombre del cliente'
    )
    
    last_name = models.CharField(
        max_length=50,
        validators=[validate_no_special_chars],
        help_text='Apellido del cliente'
    )
    
    email = models.EmailField(
        max_length=100,
        validators=[validate_email],
        help_text='Correo electrónico del cliente'
    )
    
    phone = models.CharField(
        max_length=15,
        validators=[validate_phone_number],
        help_text='Número de teléfono del cliente'
    )
    
    address = models.CharField(
        max_length=100,
        help_text='Dirección del cliente'
    )
    
    city = models.CharField(
        max_length=50,
        validators=[validate_no_special_chars],
        help_text='Ciudad del cliente'
    )
    
    state = models.CharField(
        max_length=50,
        validators=[validate_no_special_chars],
        help_text='Departamento/Estado del cliente'
    )
    
    zip_code = models.CharField(
        max_length=10,
        validators=[validate_zip_code],
        help_text='Código postal'
    )
    
    # ============================================================
    # CAMPOS DE AUDITORÍA (Capa 4 - Seguridad)
    # ============================================================
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización del registro'
    )
    
    updated_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='records_updated',
        help_text='Usuario que actualizó el registro'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el registro está activo'
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        help_text='Notas adicionales sobre el cliente'
    )
    
    # ============================================================
    # MÉTODOS DEL MODELO
    # ============================================================
    
    def __str__(self):
        """Representación legible del registro"""
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    def get_full_name(self):
        """Retorna el nombre completo (DRY)"""
        return f"{self.first_name} {self.last_name}"
    
    def get_location(self):
        """Retorna ubicación completa (DRY)"""
        return f"{self.city}, {self.state} - {self.zip_code}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe save para añadir lógica adicional
        """
        # Verificar duplicados (DRY - lógica centralizada)
        if not self.pk:  # Solo en creación
            if Record.objects.filter(email=self.email).exists():
                raise ValidationError(
                    f'Ya existe un registro con el email "{self.email}"'
                )
        super().save(*args, **kwargs)
    
    def soft_delete(self, usuario=None):
        """
        Eliminación suave (soft delete) en lugar de eliminación física
        """
        self.is_active = False
        if usuario:
            self.updated_by = usuario
        self.save()
    
    class Meta:
        verbose_name = 'Registro de Cliente'
        verbose_name_plural = 'Registros de Clientes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
        ]


# ============================================================
# 5. SEÑALES (DRY - Automatización)
# ============================================================

@receiver(post_save, sender=Usuario)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Señal para crear automáticamente un perfil cuando se crea un usuario
    Aplica el principio DRY: no repetimos esta lógica en cada vista
    """
    if created:
        PerfilUsuario.objects.create(usuario=instance)


@receiver(post_save, sender=Usuario)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Señal para guardar automáticamente el perfil cuando se guarda el usuario
    """
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


@receiver(post_save, sender=Record)
def log_creacion_record(sender, instance, created, **kwargs):
    """
    Señal para registrar la creación/actualización de records (Auditoría)
    """
    if created:
        import logging
        logger = logging.getLogger('website.security')
        logger.info(f'Record creado: {instance} por {instance.usuario}')


# ============================================================
# 6. MODELO DE ACTIVIDAD (Auditoría - Capa 4)
# ============================================================

class ActividadUsuario(models.Model):
    """
    Modelo para registrar actividades de usuarios (Auditoría)
    Aplicando SOLID: responsabilidad única de registro de actividades
    """
    
    TIPOS_ACTIVIDAD = (
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('creacion', 'Creación de Registro'),
        ('edicion', 'Edición de Registro'),
        ('eliminacion', 'Eliminación de Registro'),
        ('compra', 'Compra Realizada'),
        ('error', 'Error del Sistema'),
        ('seguridad', 'Evento de Seguridad'),
    )
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actividades'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_ACTIVIDAD
    )
    
    descripcion = models.TextField(
        help_text='Descripción detallada de la actividad'
    )
    
    ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text='Dirección IP desde la que se realizó la actividad'
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text='User Agent del navegador'
    )
    
    datos_adicionales = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos adicionales en formato JSON'
    )
    
    fecha = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha y hora de la actividad'
    )
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario} - {self.fecha}"
    
    class Meta:
        verbose_name = 'Actividad de Usuario'
        verbose_name_plural = 'Actividades de Usuarios'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['-fecha']),
            models.Index(fields=['usuario', 'tipo']),
        ]