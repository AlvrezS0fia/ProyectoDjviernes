from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .utils import no_dangerous_chars, valid_name

# ---------- FORMULARIO DE REGISTRO DE USUARIO ----------
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message='Correo electrónico no válido.'), no_dangerous_chars],
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'tu@email.com', 'autocomplete': 'email'})
    )
    first_name = forms.CharField(
        max_length=30, required=True,
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu nombre', 'autocomplete': 'given-name'})
    )
    last_name = forms.CharField(
        max_length=30, required=False,
        validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellidos (opcional)', 'autocomplete': 'family-name'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Mínimo 8 caracteres', 'autocomplete': 'new-password'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Repite tu contraseña', 'autocomplete': 'new-password'})
    )
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
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name', '').strip()

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Debe contener al menos una letra mayúscula.')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Debe contener al menos una letra minúscula.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Debe contener al menos un carácter especial.')
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']   # email como username
        if commit:
            user.save()
        return user

# ---------- FORMULARIO PARA REGISTRAR CLIENTES (Record) ----------
class RecordForm(forms.ModelForm):
    from .models import Record

    first_name = forms.CharField(
        label="", validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={"placeholder": "Nombre", "class": "form-input"})
    )
    last_name = forms.CharField(
        label="", validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={"placeholder": "Apellido", "class": "form-input"})
    )
    email = forms.EmailField(
        label="", validators=[EmailValidator(), no_dangerous_chars],
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-input"})
    )
    phone_number = forms.CharField(
        label="", validators=[no_dangerous_chars],
        widget=forms.TextInput(attrs={"placeholder": "Teléfono", "class": "form-input"})
    )
    address = forms.CharField(
        label="", validators=[no_dangerous_chars],
        widget=forms.TextInput(attrs={"placeholder": "Dirección", "class": "form-input"})
    )
    city = forms.CharField(
        label="", validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={"placeholder": "Ciudad", "class": "form-input"})
    )
    state = forms.CharField(
        label="", validators=[no_dangerous_chars, valid_name],
        widget=forms.TextInput(attrs={"placeholder": "Estado", "class": "form-input"})
    )
    zip_code = forms.CharField(
        label="", validators=[no_dangerous_chars],
        widget=forms.TextInput(attrs={"placeholder": "Código Postal", "class": "form-input"})
    )

    class Meta:
        from .models import Record
        model = Record
        fields = ["first_name", "last_name", "email", "phone_number", "address", "city", "state", "zip_code"]