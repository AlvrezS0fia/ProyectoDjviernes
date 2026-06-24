# clientes/forms.py

"""
Formularios de la aplicación clientes para ANGELOW
Define el formulario ClienteForm con validaciones personalizadas
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Cliente
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
    """
    if value and not re.match(r'^\+?[\d\s-]{7,20}$', value):
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


# ============================================================
# 2. FORMULARIO CLIENTE (DRY - ModelForm)
# ============================================================

class ClienteForm(forms.ModelForm):
    """
    Formulario para el CRUD de clientes
    
    Principios aplicados:
    - DRY: Hereda de ModelForm, no reescribimos los campos
    - SOLID: Responsabilidad única de validación de clientes
    - Seguridad: Validaciones con expresiones regulares (Capa 3)
    """
    
    # ============================================================
    # CAMPOS ADICIONALES (Opcionales)
    # ============================================================
    
    # Confirmación de email para evitar errores de tipeo
    confirmar_email = forms.EmailField(
        label="Confirmar Email",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar correo electrónico'
        }),
        help_text="Vuelve a escribir el correo electrónico para confirmar"
    )
    
    # Campo para tipo de cliente (opcional)
    tipo_cliente = forms.ChoiceField(
        label="Tipo de Cliente",
        choices=[
            ('regular', 'Regular'),
            ('vip', 'VIP'),
            ('corporativo', 'Corporativo'),
            ('distribuidor', 'Distribuidor'),
        ],
        required=False,
        initial='regular',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Cliente
        fields = [
            'nombre', 
            'email', 
            'confirmar_email',  # Campo adicional
            'telefono', 
            'direccion',
            'tipo_cliente',     # Campo adicional
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del cliente',
                'autofocus': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Calle 123 # 45-67, Ciudad'
            }),
        }
        labels = {
            'nombre': 'Nombre Completo',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'tipo_cliente': 'Tipo de Cliente',
        }
        help_texts = {
            'nombre': 'Solo letras, números, espacios y guiones.',
            'email': 'Ingresa un correo electrónico válido.',
            'telefono': 'Formato: +57 300 123 4567 (opcional).',
            'direccion': 'Dirección completa del cliente.',
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre del cliente es obligatorio.',
                'max_length': 'El nombre no puede tener más de 100 caracteres.',
            },
            'email': {
                'required': 'El correo electrónico es obligatorio.',
                'unique': 'Ya existe un cliente con este correo electrónico.',
                'invalid': 'Ingresa un correo electrónico válido.',
            },
        }

    # ============================================================
    # VALIDACIONES PERSONALIZADAS (Capa 3 - Expresiones Regulares)
    # ============================================================

    def clean_nombre(self):
        """
        Valida que el nombre solo contenga caracteres permitidos
        """
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            nombre = nombre.strip()
            return validate_no_special_chars(nombre)
        return nombre

    def clean_email(self):
        """
        Valida el formato del email y que no esté duplicado
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            validate_email(email)
            
            # Verificar duplicados (excluyendo el registro actual)
            instance = getattr(self, 'instance', None)
            if instance and instance.pk:
                # Edición: verificar que no exista otro cliente con el mismo email
                if Cliente.objects.exclude(pk=instance.pk).filter(email=email).exists():
                    raise ValidationError(
                        'Ya existe otro cliente con este correo electrónico.'
                    )
            else:
                # Creación: verificar que el email no exista
                if Cliente.objects.filter(email=email).exists():
                    raise ValidationError(
                        'Ya existe un cliente con este correo electrónico.'
                    )
            
            return email
        return email

    def clean_confirmar_email(self):
        """
        Valida que el email de confirmación coincida
        """
        email = self.cleaned_data.get('email')
        confirmar_email = self.cleaned_data.get('confirmar_email')
        
        if email and confirmar_email:
            if email != confirmar_email:
                raise ValidationError(
                    'Los correos electrónicos no coinciden.'
                )
        return confirmar_email

    def clean_telefono(self):
        """
        Valida el número de teléfono
        """
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono = telefono.strip()
            return validate_phone_number(telefono)
        return telefono

    def clean_direccion(self):
        """
        Valida que la dirección no contenga caracteres peligrosos
        """
        direccion = self.cleaned_data.get('direccion')
        if direccion:
            direccion = direccion.strip()
            if not re.match(r'^[a-zA-Z0-9\s\-_.,#áéíóúÁÉÍÓÚñÑ]+$', direccion):
                raise ValidationError(
                    'La dirección contiene caracteres no permitidos.'
                )
            return direccion
        return direccion

    def clean(self):
        """
        Validación general del formulario
        """
        cleaned_data = super().clean()
        
        # Verificar que el email no esté vacío
        email = cleaned_data.get('email')
        if not email:
            self.add_error('email', 'El correo electrónico es obligatorio.')
        
        return cleaned_data

    # ============================================================
    # MÉTODOS DE GUARDADO (DRY)
    # ============================================================

    def save(self, commit=True, usuario=None, actualizado_por=None):
        """
        Guarda el formulario con información adicional
        
        Args:
            commit: Si debe guardar en la base de datos
            usuario: Usuario que crea el cliente
            actualizado_por: Usuario que actualiza el cliente
        """
        instance = super().save(commit=False)
        
        # Asignar usuario si se proporciona
        if usuario and not instance.pk:
            instance.usuario = usuario
        
        # Asignar actualizado_por si se proporciona
        if actualizado_por:
            instance.actualizado_por = actualizado_por
        
        # Guardar el tipo de cliente del campo adicional
        tipo_cliente = self.cleaned_data.get('tipo_cliente')
        if tipo_cliente:
            instance.tipo_cliente = tipo_cliente
        
        if commit:
            instance.save()
            # Registrar auditoría
            logger.info(
                f'Cliente {"creado" if not instance.pk else "actualizado"}: '
                f'{instance.nombre} - {instance.email}'
            )
        
        return instance


# ============================================================
# 3. FORMULARIO DE FILTRO/BÚSQUEDA (Opcional)
# ============================================================

class ClienteFilterForm(forms.Form):
    """
    Formulario para filtrar clientes en el listado
    Aplicando DRY con widgets reutilizables
    """
    
    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre...'
        })
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por email...'
        })
    )
    
    tipo_cliente = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + [
            ('regular', 'Regular'),
            ('vip', 'VIP'),
            ('corporativo', 'Corporativo'),
            ('distribuidor', 'Distribuidor'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos'),
            ('activo', 'Activos'),
            ('inactivo', 'Inactivos'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


# ============================================================
# 4. FORMULARIO PARA IMPORTACIÓN MASIVA (Opcional)
# ============================================================

class ClienteImportForm(forms.Form):
    """
    Formulario para importar clientes desde archivo CSV/Excel
    """
    
    archivo = forms.FileField(
        label="Archivo de Clientes",
        help_text="Sube un archivo CSV o Excel con los datos de los clientes",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    
    delimitador = forms.ChoiceField(
        label="Delimitador CSV",
        choices=[
            (',', 'Coma (,)'),
            (';', 'Punto y coma (;)'),
            ('\t', 'Tabulador'),
        ],
        required=False,
        initial=',',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sobrescribir = forms.BooleanField(
        label="Sobrescribir clientes existentes",
        required=False,
        initial=False,
        help_text="Si hay duplicados por email, actualizar los datos existentes",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_archivo(self):
        """
        Valida que el archivo sea válido
        """
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar extensión
            nombre = archivo.name.lower()
            if not any(nombre.endswith(ext) for ext in ['.csv', '.xlsx', '.xls']):
                raise ValidationError(
                    'El archivo debe ser de tipo CSV o Excel (.csv, .xlsx, .xls)'
                )
            
            # Validar tamaño (máximo 5MB)
            if archivo.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError(
                    'El archivo no puede superar los 5MB.'
                )
        
        return archivo