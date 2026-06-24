# tienda/forms.py

"""
Formularios de la aplicación tienda para ANGELOW
Define formularios para carrito, favoritos, búsqueda y checkout
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import CarritoItem, Producto
import re
import logging

# Configurar logger para auditoría
logger = logging.getLogger('website.security')

# ============================================================
# 1. VALIDADORES PERSONALIZADOS (Expresiones Regulares - Capa 3)
# ============================================================

def validate_talla(value):
    """
    Valida que la talla sea válida
    """
    tallas_validas = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL', '4XL', '5XL', 
                      '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35',
                      '36', '37', '38', '39', '40', '41', '42', '43', '44', '45']
    
    if value not in tallas_validas:
        raise ValidationError(f'La talla "{value}" no es válida.')
    return value

def validate_cantidad(value):
    """
    Valida que la cantidad sea válida
    """
    if value < 1:
        raise ValidationError('La cantidad debe ser al menos 1.')
    if value > 10:
        raise ValidationError('No puedes agregar más de 10 unidades de este producto.')
    return value


# ============================================================
# 2. FORMULARIO PARA AGREGAR AL CARRITO (DRY - Form)
# ============================================================

class AgregarAlCarritoForm(forms.Form):
    """
    Formulario para agregar productos al carrito
    
    Principios aplicados:
    - SRP: Solo maneja la adición de productos al carrito
    - DRY: Widgets reutilizables
    - Seguridad: Validaciones con expresiones regulares (Capa 3)
    """
    
    talla = forms.ChoiceField(
        label="Talla",
        choices=[],  # Se llenan dinámicamente en el __init__
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'talla-select'
        })
    )
    
    cantidad = forms.IntegerField(
        label="Cantidad",
        initial=1,
        min_value=1,
        max_value=10,
        validators=[validate_cantidad],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 10,
            'id': 'cantidad-input'
        })
    )
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con las tallas disponibles del producto
        """
        tallas_disponibles = kwargs.pop('tallas_disponibles', [])
        super().__init__(*args, **kwargs)
        
        if tallas_disponibles:
            choices = [(talla, talla) for talla in tallas_disponibles]
            self.fields['talla'].choices = choices
            
            # Seleccionar la primera talla por defecto
            if choices:
                self.fields['talla'].initial = choices[0][0]
        else:
            self.fields['talla'].choices = [('', 'No hay tallas disponibles')]
            self.fields['talla'].widget.attrs['disabled'] = 'disabled'
    
    def clean_talla(self):
        """
        Valida que la talla sea válida
        """
        talla = self.cleaned_data.get('talla')
        if talla:
            return validate_talla(talla)
        raise ValidationError('Debes seleccionar una talla.')
    
    def clean_cantidad(self):
        """
        Valida la cantidad
        """
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad:
            return validate_cantidad(cantidad)
        return 1


# ============================================================
# 3. FORMULARIO PARA ACTUALIZAR CARRITO (DRY - ModelForm)
# ============================================================

class ActualizarCarritoForm(forms.ModelForm):
    """
    Formulario para actualizar la cantidad de un item en el carrito
    """
    
    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=0,
        max_value=10,
        validators=[validate_cantidad],
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'min': 0,
            'max': 10
        })
    )
    
    class Meta:
        model = CarritoItem
        fields = ['cantidad']
    
    def __init__(self, *args, **kwargs):
        self.producto = kwargs.pop('producto', None)
        super().__init__(*args, **kwargs)
    
    def clean_cantidad(self):
        """
        Valida que la cantidad no supere el stock disponible
        """
        cantidad = self.cleaned_data.get('cantidad')
        
        if cantidad == 0:
            return cantidad
        
        if self.producto:
            if cantidad > self.producto.stock:
                raise ValidationError(
                    f'Solo hay {self.producto.stock} unidades disponibles.'
                )
        
        return cantidad


# ============================================================
# 4. FORMULARIO DE BÚSQUEDA Y FILTRO (DRY - Form)
# ============================================================

class ProductoFilterForm(forms.Form):
    """
    Formulario para filtrar y buscar productos
    
    Principios aplicados:
    - SRP: Solo maneja la búsqueda y filtrado
    - DRY: Campos reutilizables
    """
    
    q = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar productos...',
            'aria-label': 'Buscar'
        })
    )
    
    categoria = forms.ChoiceField(
        required=False,
        label="Categoría",
        choices=[],  # Se llenan dinámicamente
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    precio_min = forms.DecimalField(
        required=False,
        label="Precio Mínimo",
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Desde'
        })
    )
    
    precio_max = forms.DecimalField(
        required=False,
        label="Precio Máximo",
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hasta'
        })
    )
    
    ordenar = forms.ChoiceField(
        required=False,
        label="Ordenar por",
        choices=[
            ('', 'Relevancia'),
            ('precio_asc', 'Precio: Menor a Mayor'),
            ('precio_desc', 'Precio: Mayor a Menor'),
            ('nombre_asc', 'Nombre: A-Z'),
            ('nombre_desc', 'Nombre: Z-A'),
            ('rating_desc', 'Mejor Calificados'),
            ('nuevos', 'Más Recientes'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    talla = forms.ChoiceField(
        required=False,
        label="Talla",
        choices=[
            ('', 'Todas'),
            ('XS', 'XS'),
            ('S', 'S'),
            ('M', 'M'),
            ('L', 'L'),
            ('XL', 'XL'),
            ('XXL', 'XXL'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    en_oferta = forms.BooleanField(
        required=False,
        label="Solo en oferta",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con las categorías disponibles
        """
        categorias = kwargs.pop('categorias', [])
        super().__init__(*args, **kwargs)
        
        if categorias:
            choices = [('', 'Todas las categorías')] + [
                (cat.slug, cat.nombre) for cat in categorias
            ]
            self.fields['categoria'].choices = choices
    
    def clean_precio_min(self):
        """
        Valida que el precio mínimo sea positivo
        """
        precio_min = self.cleaned_data.get('precio_min')
        if precio_min is not None and precio_min < 0:
            raise ValidationError('El precio mínimo no puede ser negativo.')
        return precio_min
    
    def clean_precio_max(self):
        """
        Valida que el precio máximo sea positivo y mayor que el mínimo
        """
        precio_max = self.cleaned_data.get('precio_max')
        precio_min = self.cleaned_data.get('precio_min')
        
        if precio_max is not None:
            if precio_max < 0:
                raise ValidationError('El precio máximo no puede ser negativo.')
            
            if precio_min is not None and precio_max < precio_min:
                raise ValidationError('El precio máximo debe ser mayor que el mínimo.')
        
        return precio_max
    
    def clean(self):
        """
        Validación general del formulario
        """
        cleaned_data = super().clean()
        
        # Validar que los precios sean números válidos
        precio_min = cleaned_data.get('precio_min')
        precio_max = cleaned_data.get('precio_max')
        
        if precio_min == '':
            cleaned_data['precio_min'] = None
        if precio_max == '':
            cleaned_data['precio_max'] = None
        
        return cleaned_data


# ============================================================
# 5. FORMULARIO DE CHECKOUT (DRY - Form)
# ============================================================

class CheckoutForm(forms.Form):
    """
    Formulario para el proceso de checkout/compra
    
    Principios aplicados:
    - SRP: Solo maneja la información de compra
    - DRY: Widgets reutilizables
    - Seguridad: Validaciones con expresiones regulares (Capa 3)
    """
    
    # ============================================================
    # INFORMACIÓN DE ENVÍO
    # ============================================================
    
    nombre_completo = forms.CharField(
        max_length=100,
        label="Nombre Completo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre completo del destinatario'
        })
    )
    
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    
    telefono = forms.CharField(
        max_length=20,
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+57 300 123 4567'
        })
    )
    
    direccion = forms.CharField(
        label="Dirección",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Calle 123 # 45-67'
        })
    )
    
    ciudad = forms.CharField(
        max_length=50,
        label="Ciudad",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Medellín'
        })
    )
    
    estado = forms.CharField(
        max_length=50,
        label="Departamento/Estado",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Antioquia'
        })
    )
    
    codigo_postal = forms.CharField(
        max_length=10,
        label="Código Postal",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '050001'
        })
    )
    
    # ============================================================
    # INFORMACIÓN DE ENVÍO ADICIONAL
    # ============================================================
    
    instrucciones_entrega = forms.CharField(
        required=False,
        label="Instrucciones de Entrega",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Instrucciones adicionales para el repartidor...'
        })
    )
    
    # ============================================================
    # INFORMACIÓN DE PAGO
    # ============================================================
    
    metodo_pago = forms.ChoiceField(
        label="Método de Pago",
        choices=[
            ('', 'Selecciona un método de pago'),
            ('efectivo', 'Pago en Efectivo (Contraentrega)'),
            ('tarjeta', 'Tarjeta de Crédito/Débito'),
            ('nequi', 'Nequi'),
            ('daviplata', 'Daviplata'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # ============================================================
    # TÉRMINOS Y CONDICIONES
    # ============================================================
    
    aceptar_terminos = forms.BooleanField(
        required=True,
        label='Acepto los Términos y Condiciones de compra.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    # ============================================================
    # VALIDACIONES PERSONALIZADAS (Capa 3 - Expresiones Regulares)
    # ============================================================
    
    def clean_nombre_completo(self):
        """Valida que el nombre solo contenga caracteres permitidos"""
        nombre = self.cleaned_data.get('nombre_completo')
        if nombre:
            nombre = nombre.strip()
            if not re.match(r'^[a-zA-Z\s\-_áéíóúÁÉÍÓÚñÑ.]+$', nombre):
                raise ValidationError(
                    'El nombre solo puede contener letras, espacios y guiones.'
                )
            return nombre
        return nombre
    
    def clean_email(self):
        """Valida el formato del email"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError(
                    'Ingresa un correo electrónico válido.'
                )
            return email
        return email
    
    def clean_telefono(self):
        """Valida el número de teléfono"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            telefono = telefono.strip()
            if not re.match(r'^\+?[\d\s-]{7,20}$', telefono):
                raise ValidationError(
                    'Ingresa un número de teléfono válido (mínimo 7 dígitos).'
                )
            return telefono
        return telefono
    
    def clean_codigo_postal(self):
        """Valida el código postal"""
        codigo = self.cleaned_data.get('codigo_postal')
        if codigo:
            codigo = codigo.strip()
            if codigo and not re.match(r'^\d{5,10}$', codigo):
                raise ValidationError(
                    'El código postal debe contener solo números (5-10 dígitos).'
                )
            return codigo
        return codigo
    
    def clean_aceptar_terminos(self):
        """Valida que se acepten los términos"""
        aceptar = self.cleaned_data.get('aceptar_terminos')
        if not aceptar:
            raise ValidationError(
                'Debes aceptar los Términos y Condiciones para continuar.'
            )
        return aceptar


# ============================================================
# 6. FORMULARIO PARA AGREGAR FAVORITO (DRY - Form)
# ============================================================

class FavoritoForm(forms.Form):
    """
    Formulario para agregar/quitar productos de favoritos
    """
    
    producto_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    
    def clean_producto_id(self):
        """
        Valida que el producto exista
        """
        producto_id = self.cleaned_data.get('producto_id')
        if producto_id:
            try:
                producto = Producto.objects.get(id=producto_id)
                return producto_id
            except Producto.DoesNotExist:
                raise ValidationError('El producto no existe.')
        return producto_id


# ============================================================
# 7. FORMULARIO PARA COMENTARIOS/RESEÑAS (DRY - Form)
# ============================================================

class ReseñaForm(forms.Form):
    """
    Formulario para agregar reseñas a productos
    """
    
    rating = forms.ChoiceField(
        label="Calificación",
        choices=[
            (5, '⭐⭐⭐⭐⭐ Excelente'),
            (4, '⭐⭐⭐⭐ Muy Bueno'),
            (3, '⭐⭐⭐ Bueno'),
            (2, '⭐⭐ Regular'),
            (1, '⭐ Malo'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    titulo = forms.CharField(
        max_length=100,
        label="Título de la Reseña",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título de tu reseña (opcional)'
        })
    )
    
    comentario = forms.CharField(
        label="Comentario",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Cuéntanos tu experiencia con el producto...'
        })
    )
    
    # ============================================================
    # VALIDACIONES
    # ============================================================
    
    def clean_comentario(self):
        """
        Valida que el comentario no sea muy corto
        """
        comentario = self.cleaned_data.get('comentario')
        if comentario:
            if len(comentario.strip()) < 10:
                raise ValidationError(
                    'El comentario debe tener al menos 10 caracteres.'
                )
            return comentario.strip()
        return comentario