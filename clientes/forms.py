# clientes/forms.py

from django import forms
from .models import Cliente
from website.validators import validate_no_special_chars, validate_phone, validate_email


class ClienteForm(forms.ModelForm):
    """
    Formulario para la gestión de clientes
    """
    class Meta:
        model = Cliente
        fields = [
            'identificacion', 'nombre', 'apellido', 'email', 
            'telefono', 'direccion', 'ciudad', 'tipo_cliente', 'activo'
        ]
        widgets = {
            'identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1234567890',
                'required': True
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente',
                'required': True
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '3001234567'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección del cliente'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'tipo_cliente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'identificacion': 'Identificación',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'tipo_cliente': 'Tipo de Cliente',
            'activo': 'Cliente Activo',
        }

    def clean_identificacion(self):
        identificacion = self.cleaned_data.get('identificacion')
        if identificacion:
            # Validar que solo contenga caracteres válidos
            if not identificacion.isalnum():
                raise forms.ValidationError('La identificación solo debe contener letras y números.')
            
            # Verificar unicidad
            if Cliente.objects.filter(identificacion=identificacion).exists():
                raise forms.ValidationError('Ya existe un cliente con esta identificación.')
        return identificacion

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            validate_no_special_chars(nombre)
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if apellido:
            validate_no_special_chars(apellido)
        return apellido

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validate_email(email)
            # Verificar unicidad
            if Cliente.objects.filter(email=email).exists():
                raise forms.ValidationError('Ya existe un cliente con este correo electrónico.')
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            validate_phone(telefono)
        return telefono