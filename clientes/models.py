# clientes/models.py

"""
Modelos de la aplicación clientes para ANGELOW
Define el modelo Cliente para el CRM (Customer Relationship Management)
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import re
import logging

# Configurar logger para auditoría
logger = logging.getLogger('website.security')

# ============================================================
# 1. VALIDADORES PERSONALIZADOS (Expresiones Regulares - Capa 3)
# ============================================================

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
    Longitud: 7-20 caracteres
    """
    if not re.match(r'^\+?[\d\s-]{7,20}$', value):
        raise ValidationError(
            'Ingresa un número de teléfono válido (mínimo 7 dígitos).'
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

def validate_address(value):
    """
    Valida dirección (no permite caracteres peligrosos)
    """
    if not re.match(r'^[a-zA-Z0-9\s\-_.,#áéíóúÁÉÍÓÚñÑ]+$', value):
        raise ValidationError(
            'La dirección contiene caracteres no permitidos.'
        )
    return value

# ============================================================
# 2. MODELO CLIENTE (Single Responsibility - SRP)
# ============================================================

class Cliente(models.Model):
    """
    Modelo para la gestión de clientes en el CRM
    
    Principios aplicados:
    - SRP: Maneja solo información de clientes
    - DRY: Reutiliza validadores personalizados
    - Seguridad: Validaciones con regex (Capa 3)
    - Auditoría: Registro de creación y modificación (Capa 4)
    """
    
    # ============================================================
    # RELACIONES (Integración con sistema de usuarios)
    # ============================================================
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clientes',
        null=True,
        blank=True,
        help_text='Usuario que creó o gestiona este cliente'
    )
    
    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================
    nombre = models.CharField(
        max_length=100,
        validators=[validate_no_special_chars],
        help_text='Nombre completo del cliente'
    )
    
    email = models.EmailField(
        unique=True,
        validators=[validate_email],
        help_text='Correo electrónico del cliente (único)'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        help_text='Número de teléfono del cliente'
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        validators=[validate_address],
        help_text='Dirección del cliente'
    )
    
    # ============================================================
    # CAMPOS DE AUDITORÍA (Capa 4 - Seguridad)
    # ============================================================
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha en que se registró el cliente'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización del registro'
    )
    
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_actualizados',
        help_text='Usuario que actualizó el registro'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el cliente está activo'
    )
    
    # ============================================================
    # CAMPOS ADICIONALES PARA MEJOR GESTIÓN
    # ============================================================
    tipo_cliente = models.CharField(
        max_length=20,
        choices=[
            ('regular', 'Regular'),
            ('vip', 'VIP'),
            ('corporativo', 'Corporativo'),
            ('distribuidor', 'Distribuidor'),
        ],
        default='regular',
        help_text='Tipo o categoría del cliente'
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        help_text='Notas adicionales sobre el cliente'
    )
    
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de nacimiento del cliente'
    )
    
    # ============================================================
    # MÉTODOS DEL MODELO
    # ============================================================
    
    def __str__(self):
        """Representación legible del cliente"""
        return f"{self.nombre} - {self.email}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo (DRY)"""
        return self.nombre
    
    def get_email_display(self):
        """Retorna el email para mostrar"""
        return self.email
    
    def get_telefono_display(self):
        """Retorna el teléfono formateado"""
        return self.telefono or 'No disponible'
    
    def get_direccion_display(self):
        """Retorna la dirección formateada"""
        return self.direccion or 'No disponible'
    
    def get_tipo_cliente_display(self):
        """Retorna el tipo de cliente en español"""
        tipos = {
            'regular': 'Regular',
            'vip': 'VIP',
            'corporativo': 'Corporativo',
            'distribuidor': 'Distribuidor',
        }
        return tipos.get(self.tipo_cliente, self.tipo_cliente)
    
    def es_vip(self):
        """Verifica si el cliente es VIP"""
        return self.tipo_cliente == 'vip'
    
    def es_activo(self):
        """Verifica si el cliente está activo"""
        return self.is_active
    
    def activar(self):
        """Activa el cliente"""
        self.is_active = True
        self.save()
    
    def desactivar(self):
        """Desactiva el cliente (soft delete)"""
        self.is_active = False
        self.save()
    
    def soft_delete(self, usuario=None):
        """
        Eliminación suave (soft delete) en lugar de eliminación física
        """
        self.is_active = False
        if usuario:
            self.actualizado_por = usuario
        self.save()
        logger.info(f'Cliente desactivado: {self.nombre} por {usuario}')
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe save para añadir lógica adicional
        """
        # Validar email único (DRY - lógica centralizada)
        if not self.pk:  # Solo en creación
            if Cliente.objects.filter(email=self.email).exists():
                raise ValidationError(
                    f'Ya existe un cliente con el email "{self.email}"'
                )
        
        # Limpiar espacios en blanco (DRY)
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.email:
            self.email = self.email.lower().strip()
        if self.telefono:
            self.telefono = self.telefono.strip()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['nombre']),
            models.Index(fields=['-fecha_registro']),
            models.Index(fields=['is_active']),
            models.Index(fields=['tipo_cliente']),
        ]


# ============================================================
# 3. SEÑALES (DRY - Automatización y Auditoría)
# ============================================================

@receiver(pre_save, sender=Cliente)
def cliente_pre_save(sender, instance, **kwargs):
    """
    Señal que se ejecuta antes de guardar un cliente
    Valida que el email no esté duplicado
    """
    if instance.pk:
        # Verificar si el email está siendo cambiado
        original = Cliente.objects.get(pk=instance.pk)
        if original.email != instance.email:
            if Cliente.objects.filter(email=instance.email).exists():
                raise ValidationError(
                    f'Ya existe un cliente con el email "{instance.email}"'
                )


@receiver(post_save, sender=Cliente)
def cliente_post_save(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta después de guardar un cliente
    Registra la actividad en el log (Capa 4 - Auditoría)
    """
    if created:
        logger.info(
            f'Cliente creado: {instance.nombre} - {instance.email} '
            f'por {instance.usuario}'
        )
    else:
        # Verificar si hubo cambios importantes
        try:
            original = Cliente.objects.get(pk=instance.pk)
            cambios = []
            if original.nombre != instance.nombre:
                cambios.append(f'nombre: {original.nombre} -> {instance.nombre}')
            if original.email != instance.email:
                cambios.append(f'email: {original.email} -> {instance.email}')
            if original.telefono != instance.telefono:
                cambios.append(f'teléfono: {original.telefono} -> {instance.telefono}')
            
            if cambios:
                logger.info(
                    f'Cliente actualizado: {instance.nombre} - '
                    f'Cambios: {", ".join(cambios)} '
                    f'por {instance.actualizado_por}'
                )
        except Cliente.DoesNotExist:
            pass


@receiver(post_save, sender=Cliente)
def cliente_crear_actividad(sender, instance, created, **kwargs):
    """
    Señal para registrar actividad de cliente en el modelo de auditoría
    """
    if created:
        from website.models import ActividadUsuario
        if instance.usuario:
            ActividadUsuario.objects.create(
                usuario=instance.usuario,
                tipo='creacion',
                descripcion=f'Cliente creado: {instance.nombre} - {instance.email}',
                datos_adicionales={
                    'cliente_id': instance.id,
                    'cliente_nombre': instance.nombre,
                    'cliente_email': instance.email,
                }
            )