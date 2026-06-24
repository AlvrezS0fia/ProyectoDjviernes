import re
from django.core.exceptions import ValidationError


def no_dangerous_chars(value):
    if re.search(r'[<>\'";`&|$(){}[\]]', value):
        raise ValidationError('No se permiten caracteres especiales como < > \' " ; ` & | $ ( ) { } [ ]')
    if '\r' in value or '\n' in value:
        raise ValidationError('No se permiten saltos de línea.')


def valid_name(value):
    if not re.match(r"^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s\-']+$", value):
        raise ValidationError('Ingrese un nombre válido (solo letras, espacios, guiones y apóstrofes).')