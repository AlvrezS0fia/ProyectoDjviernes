# website/forms.py

"""
Formularios de la aplicación website para ANGELOW
Define formularios de registro, login y gestión de usuarios
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .utils import no_dangerous_chars, valid_name, validate_password_complexity
from .models import Usuario, Record
import re
import logging

# Configurar logger para auditoría
logger = logging.getLogger('website.security')

# Obtener el modelo de usuario personalizado
User = get_user_model()

# ============================================================
# 1. FORMULARIO DE REGISTRO DE USUARIO (DRY - UserCreationForm)
# ============================================================

class RegisterForm(UserCreationForm):
    """
    Formulario de registro de usuarios
    
    Principios aplicados:
    - DRY: Hereda de UserCreationForm, no reescribimos lo que ya existe
    - SOLID: Responsabilidad única de registro de usuarios
    - Seguridad: Validaciones con expresiones regulares (Capa 3)
    """
    
    # ============================================================
    # CAMPOS DEL FORMULARIO
    # ============================================================
    
    email = forms.EmailField(
        required=True,
        validators=[
            EmailValidator(message='Correo electrónico no válido.'),
            no_dangerous_chars
        ],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
            'autocomplete': 'email'
        }),
        label='Correo Electrónico'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre',
            'autocomplete': 'given-name'
        }),
        label='Nombre'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos (opcional)',
            'autocomplete': 'family-name'
        }),
        label='Apellidos'
    )
    
    telefono = forms.CharField(
        max_length=20,
        required=False,
        validators=[no_dangerous_chars],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+57 300 123 4567',
            'autocomplete': 'tel'
        }),
        label='Teléfono',
        help_text='Opcional. Formato: +57 300 123 4567'
    )
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password'
        }),
        help_text='Debe tener al menos 8 caracteres, mayúsculas, minúsculas y caracteres especiales.'
    )
    
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña',
            'autocomplete': 'new-password'
        })
    )
    
    # ============================================================
    # CAMPOS ADICIONALES (Opcionales)
    # ============================================================
    
    subscribe = forms.BooleanField(
        required=False,
        label='Me gustaría recibir noticias sobre productos y servicios de Angelow.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    terms = forms.BooleanField(
        required=True,
        label='He leído y acepto los Términos y Condiciones de Angelow.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User  # Usa el modelo personalizado
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'telefono',
            'password1', 
            'password2'
        ]

    # ============================================================
    # VALIDACIONES PERSONALIZADAS (Capa 3 - Expresiones Regulares)
    # ============================================================

    def clean_email(self):
        """
        Valida que el email sea único y tenga formato válido
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            
            # Verificar que no exista otro usuario con este email
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    'Este correo electrónico ya está registrado.'
                )
            
            # Validar formato con regex adicional
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError(
                    'Ingresa un correo electrónico válido.'
                )
            
            return email
        return email

    def clean_first_name(self):
        """
        Limpia y valida el nombre
        """
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            return first_name.strip()
        return first_name

    def clean_last_name(self):
        """
        Limpia y valida el apellido
        """
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            return last_name.strip()
        return ''

    def clean_telefono(self):
        """
        Valida el número de teléfono
        """
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono = telefono.strip()
            # Validar formato de teléfono
            if not re.match(r'^\+?[\d\s-]{7,20}$', telefono):
                raise ValidationError(
                    'Ingresa un número de teléfono válido (mínimo 7 dígitos).'
                )
            return telefono
        return telefono

    def clean_password1(self):
        """
        Valida la complejidad de la contraseña
        """
        password = self.cleaned_data.get('password1')
        if password:
            # Usar el validador centralizado
            return validate_password_complexity(password)
        return password

    def clean_terms(self):
        """
        Valida que se acepten los términos
        """
        terms = self.cleaned_data.get('terms')
        if not terms:
            raise ValidationError(
                'Debes aceptar los Términos y Condiciones para registrarte.'
            )
        return terms

    def clean(self):
        """
        Validación general del formulario
        """
        cleaned_data = super().clean()
        
        # Verificar que las contraseñas coincidan
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        
        return cleaned_data

    # ============================================================
    # MÉTODO DE GUARDADO
    # ============================================================

    def save(self, commit=True):
        """
        Guarda el usuario con los datos del formulario
        """
        user = super().save(commit=False)
        
        # Asignar email como username (para login con email)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        
        # Asignar rol por defecto (usuario regular)
        user.rol = 'user'
        
        # Asignar teléfono si se proporcionó
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            user.telefono = telefono
        
        if commit:
            user.save()
            # Registrar auditoría (Capa 4)
            logger.info(f'Usuario registrado: {user.email} - {user.get_full_name()}')
        
        return user


# ============================================================
# 2. FORMULARIO DE LOGIN (Personalizado)
# ============================================================

class LoginForm(AuthenticationForm):
    """
    Formulario de inicio de sesión
    
    Principios aplicados:
    - DRY: Hereda de AuthenticationForm
    - Seguridad: Mensajes de error genéricos (Capa 2)
    """
    
    username = forms.CharField(
        label='Correo Electrónico o Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com o usuario',
            'autocomplete': 'username',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu contraseña',
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        label='Recordarme',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error
        self.error_messages['invalid_login'] = (
            'Usuario o contraseña incorrectos. Verifica tus credenciales.'
        )
        self.error_messages['inactive'] = (
            'Esta cuenta está desactivada. Contacta al administrador.'
        )

    def clean_username(self):
        """
        Permite login con email o username
        """
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip().lower()
            
            # Si es un email, buscar el usuario por email
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    return user.username
                except User.DoesNotExist:
                    pass
            
            return username
        return username


# ============================================================
# 3. FORMULARIO PARA REGISTRAR CLIENTES (Record)
# ============================================================

class RecordForm(forms.ModelForm):
    """
    Formulario para el modelo Record (Clientes en CRM)
    Aplicando DRY: Hereda de ModelForm
    
    Principios aplicados:
    - DRY: No reescribimos los campos que ya existen en el modelo
    - Seguridad: Validaciones con expresiones regulares (Capa 3)
    """
    
    # ============================================================
    # CAMPOS DEL FORMULARIO (Personalizados con validadores)
    # ============================================================
    
    first_name = forms.CharField(
        label="Nombre",
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={
            "placeholder": "Nombre",
            "class": "form-control",
            "autofocus": True
        })
    )
    
    last_name = forms.CharField(
        label="Apellido",
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={
            "placeholder": "Apellido",
            "class": "form-control"
        })
    )
    
    email = forms.EmailField(
        label="Correo Electrónico",
        validators=[EmailValidator(), no_dangerous_chars],
        widget=forms.EmailInput(attrs={
            "placeholder": "Email",
            "class": "form-control"
        })
    )
    
    phone = forms.CharField(  # Cambiado de 'phone_number' a 'phone'
        label="Teléfono",
        validators=[no_dangerous_chars],
        widget=forms.TextInput(attrs={
            "placeholder": "Teléfono",
            "class": "form-control"
        })
    )
    
    address = forms.CharField(
        label="Dirección",
        validators=[no_dangerous_chars],
        widget=forms.TextInput(attrs={
            "placeholder": "Dirección",
            "class": "form-control"
        })
    )
    
    city = forms.CharField(
        label="Ciudad",
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={
            "placeholder": "Ciudad",
            "class": "form-control"
        })
    )
    
    state = forms.CharField(
        label="Estado/Departamento",
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={
            "placeholder": "Estado",
            "class": "form-control"
        })
    )
    
    zip_code = forms.CharField(
        label="Código Postal",
        validators=[no_dangerous_chars],
        widget=forms.TextInput(attrs={
            "placeholder": "Código Postal",
            "class": "form-control"
        })
    )

    class Meta:
        from .models import Record
        model = Record
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone',      # <--- CAMBIADO: era 'phone_number'
            'address', 
            'city', 
            'state', 
            'zip_code'
        ]

    # ============================================================
    # VALIDACIONES PERSONALIZADAS
    # ============================================================

    def clean_email(self):
        """
        Valida que el email sea único
        """
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            
            # Verificar duplicados (excluyendo el registro actual)
            instance = getattr(self, 'instance', None)
            if instance and instance.pk:
                if Record.objects.exclude(pk=instance.pk).filter(email=email).exists():
                    raise ValidationError(
                        'Ya existe un registro con este correo electrónico.'
                    )
            else:
                if Record.objects.filter(email=email).exists():
                    raise ValidationError(
                        'Ya existe un registro con este correo electrónico.'
                    )
            
            return email
        return email

    def clean_phone(self):
        """
        Valida el número de teléfono
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = phone.strip()
            if not re.match(r'^\+?[\d\s-]{7,20}$', phone):
                raise ValidationError(
                    'Ingresa un número de teléfono válido (mínimo 7 dígitos).'
                )
            return phone
        return phone

    def clean_zip_code(self):
        """
        Valida el código postal
        """
        zip_code = self.cleaned_data.get('zip_code')
        if zip_code:
            zip_code = zip_code.strip()
            if not re.match(r'^\d{5,10}$', zip_code):
                raise ValidationError(
                    'El código postal debe contener solo números (5-10 dígitos).'
                )
            return zip_code
        return zip_code

    def save(self, commit=True, usuario=None):
        """
        Guarda el registro con información adicional
        """
        instance = super().save(commit=False)
        
        # Asignar usuario si se proporciona
        if usuario:
            instance.usuario = usuario
        
        if commit:
            instance.save()
            logger.info(f'Record creado/actualizado: {instance.email} por {usuario}')
        
        return instance


# ============================================================
# 4. FORMULARIO DE ACTUALIZACIÓN DE PERFIL
# ============================================================

class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulario para actualizar el perfil del usuario
    """
    
    first_name = forms.CharField(
        max_length=30,
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tus apellidos'
        })
    )
    
    telefono = forms.CharField(
        max_length=20,
        required=False,
        validators=[no_dangerous_chars],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+57 300 123 4567'
        })
    )
    
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Tu dirección'
        })
    )
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'telefono', 'direccion']

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono = telefono.strip()
            if not re.match(r'^\+?[\d\s-]{7,20}$', telefono):
                raise ValidationError(
                    'Ingresa un número de teléfono válido.'
                )
            return telefono
        return telefono

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            # Actualizar perfil si existe
            if hasattr(user, 'perfil'):
                perfil = user.perfil
                if 'avatar' in self.cleaned_data:
                    perfil.avatar = self.cleaned_data.get('avatar')
                perfil.save()
        
        return user