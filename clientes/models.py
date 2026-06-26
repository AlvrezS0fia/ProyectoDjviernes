# clientes/models.py

from django.db import models
from django.core.exceptions import ValidationError
import re


def validate_no_special_chars(value):
    """Valida que el texto no contenga caracteres especiales peligrosos"""
    if value:
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s.,\-]+$', value):
            raise ValidationError('El campo no puede contener caracteres especiales.')


class Cliente(models.Model):
    """
    Modelo para gestionar clientes
    """
    TIPO_CLIENTE_CHOICES = (
        ('regular', 'Regular'),
        ('vip', 'VIP'),
        ('empresa', 'Empresa'),
    )
    
    identificacion = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Identificación",
        help_text="Número de identificación único del cliente"
    )
    nombre = models.CharField(
        max_length=100, 
        verbose_name="Nombre",
        help_text="Nombre del cliente"
    )
    apellido = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Apellido",
        help_text="Apellido del cliente"
    )
    email = models.EmailField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name="Correo Electrónico",
        help_text="Correo electrónico del cliente"
    )
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Teléfono",
        help_text="Número de teléfono del cliente"
    )
    direccion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Dirección",
        help_text="Dirección del cliente"
    )
    ciudad = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Ciudad",
        help_text="Ciudad del cliente"
    )
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE_CHOICES,
        default='regular',
        verbose_name="Tipo de Cliente",
        help_text="Tipo de cliente (Regular, VIP o Empresa)"
    )
    activo = models.BooleanField(
        default=True, 
        verbose_name="Activo",
        help_text="Indica si el cliente está activo"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Registro"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, 
        verbose_name="Fecha de Actualización"
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}".strip()

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.nombre} {self.apellido}".strip()

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['identificacion']),
            models.Index(fields=['email']),
        ]