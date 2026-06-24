# website/utils.py

"""
Funciones de utilidad para la aplicación website
Validaciones con expresiones regulares (Capa 3 - Seguridad)
Aplicando principios DRY y SOLID
"""

import re
from django.core.exceptions import ValidationError

# ============================================================
# 1. VALIDADORES CON EXPRESIONES REGULARES (Capa 3)
# ============================================================

def no_dangerous_chars(value):
    """
    Valida que no contenga caracteres peligrosos para seguridad
    Permite: letras, números, espacios, guiones, puntos, arroba, guión bajo
    """
    if not re.match(r'^[a-zA-Z0-9\s\-_@.áéíóúÁÉÍÓÚñÑ]+$', value):
        raise ValidationError(
            'El campo contiene caracteres no permitidos. '
            'Solo se permiten letras, números, espacios, guiones y puntos.'
        )
    return value

def valid_name(value):
    """
    Valida que el nombre solo contenga letras, espacios y caracteres válidos
    """
    if not re.match(r'^[a-zA-Z\s\-_áéíóúÁÉÍÓÚñÑ.]+$', value):
        raise ValidationError(
            'El nombre solo puede contener letras, espacios, guiones y puntos.'
        )
    return value

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

def validate_password_complexity(value):
    """
    Valida la complejidad de la contraseña con expresiones regulares
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    errors = []
    
    if len(value) < 8:
        errors.append('La contraseña debe tener al menos 8 caracteres.')
    
    if not re.search(r'[A-Z]', value):
        errors.append('La contraseña debe contener al menos una letra mayúscula.')
    
    if not re.search(r'[a-z]', value):
        errors.append('La contraseña debe contener al menos una letra minúscula.')
    
    if not re.search(r'[0-9]', value):
        errors.append('La contraseña debe contener al menos un número.')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        errors.append('La contraseña debe contener al menos un carácter especial.')
    
    if errors:
        raise ValidationError(' '.join(errors))
    
    return value

def validate_no_especiales(value):
    """
    Valida que no contenga caracteres especiales (solo alfanumérico y espacios)
    """
    if not re.match(r'^[a-zA-Z0-9\s]+$', value):
        raise ValidationError(
            'Este campo solo puede contener letras, números y espacios.'
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

def validate_address(value):
    """
    Valida dirección (permite números, letras, espacios, guiones, puntos, comas y #)
    """
    if not re.match(r'^[a-zA-Z0-9\s\-_.,#áéíóúÁÉÍÓÚñÑ]+$', value):
        raise ValidationError(
            'La dirección contiene caracteres no permitidos.'
        )
    return value

# ============================================================
# 2. FUNCIONES DE UTILIDAD (DRY)
# ============================================================

def sanitize_string(value):
    """
    Limpia y sanitiza un string (DRY)
    """
    if value:
        # Eliminar espacios al inicio y final
        value = value.strip()
        # Eliminar múltiples espacios
        value = ' '.join(value.split())
        return value
    return value

def sanitize_email(value):
    """
    Limpia y sanitiza un email (DRY)
    """
    if value:
        value = value.strip().lower()
        return value
    return value

def get_client_ip(request):
    """
    Obtiene la IP real del cliente considerando proxies (DRY)
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')

def truncate_text(text, max_length=100):
    """
    Trunca un texto a una longitud máxima (DRY)
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

# ============================================================
# 3. VALIDADOR PARA AUTH_PASSWORD_VALIDATORS
# ============================================================

class PasswordComplexityValidator:
    """
    Validador de complejidad de contraseña para usar en AUTH_PASSWORD_VALIDATORS
    """
    
    def validate(self, password, user=None):
        """
        Valida la complejidad de la contraseña
        """
        return validate_password_complexity(password)
    
    def get_help_text(self):
        """
        Texto de ayuda para el usuario
        """
        return (
            "Tu contraseña debe tener al menos 8 caracteres, incluir al menos una "
            "mayúscula, una minúscula, un número y un carácter especial."
        )