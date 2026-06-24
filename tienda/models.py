# tienda/models.py

"""
Modelos de la aplicación tienda para ANGELOW
Define Categorías, Productos, Carrito, CarritoItem y Favoritos
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete
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
    """
    if not re.match(r'^[a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ.]+$', value):
        raise ValidationError(
            'Este campo solo puede contener letras, números, espacios, '
            'guiones y puntos.'
        )
    return value

def validate_slug(value):
    """
    Valida que el slug solo contenga caracteres permitidos
    """
    if not re.match(r'^[a-zA-Z0-9\-_]+$', value):
        raise ValidationError(
            'El slug solo puede contener letras, números, guiones y guiones bajos.'
        )
    return value

def validate_tallas(value):
    """
    Valida que las tallas sean válidas
    """
    tallas_validas = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL', '4XL', '5XL', 
                      '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35',
                      '36', '37', '38', '39', '40', '41', '42', '43', '44', '45']
    
    if not isinstance(value, list):
        raise ValidationError('Las tallas deben ser una lista.')
    
    for talla in value:
        if talla not in tallas_validas:
            raise ValidationError(f'La talla "{talla}" no es válida.')
    
    return value

# ============================================================
# 2. MODELO CATEGORÍA
# ============================================================

class Categoria(models.Model):
    """
    Modelo para categorías de productos
    """
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        validators=[validate_no_special_chars],
        help_text='Nombre de la categoría'
    )
    
    slug = models.SlugField(
        unique=True,
        blank=True,
        validators=[validate_slug],
        help_text='URL amigable para la categoría'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción de la categoría'
    )
    
    icono = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Clase de Font Awesome (ej: fa-tshirt)'
    )
    
    imagen = models.ImageField(
        upload_to='categorias/',
        blank=True,
        null=True,
        help_text='Imagen representativa de la categoría'
    )
    
    orden = models.PositiveIntegerField(
        default=0,
        help_text='Orden de visualización'
    )
    
    es_activa = models.BooleanField(
        default=True,
        help_text='Indica si la categoría está activa'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización'
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['orden', 'nombre']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['es_activa']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# ============================================================
# 3. MODELO PRODUCTO
# ============================================================

class Producto(models.Model):
    """
    Modelo para productos de la tienda
    """
    
    # INFORMACIÓN BÁSICA
    nombre = models.CharField(
        max_length=200,
        validators=[validate_no_special_chars],
        help_text='Nombre del producto'
    )
    
    slug = models.SlugField(
        unique=True,
        blank=True,
        validators=[validate_slug],
        help_text='URL amigable para el producto'
    )
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='productos',
        help_text='Categoría del producto'
    )
    
    subcategoria = models.CharField(
        max_length=100,
        blank=True,
        validators=[validate_no_special_chars],
        help_text='Subcategoría del producto'
    )
    
    # PRECIO Y DESCRIPCIÓN
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        help_text='Precio del producto'
    )
    
    precio_oferta = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text='Precio en oferta (si aplica)'
    )
    
    descripcion = models.TextField(
        help_text='Descripción detallada del producto'
    )
    
    caracteristicas = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de características del producto'
    )
    
    # INVENTARIO Y TALLAS
    tallas = models.JSONField(
        default=list,
        validators=[validate_tallas],
        help_text='Lista de tallas disponibles (ej: ["S", "M", "L"])'
    )
    
    stock = models.PositiveIntegerField(
        default=0,
        help_text='Cantidad disponible en inventario'
    )
    
    stock_minimo = models.PositiveIntegerField(
        default=5,
        help_text='Stock mínimo para alerta'
    )
    
    # IMÁGENES
    imagen_principal = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        help_text='Imagen principal del producto'
    )
    
    imagenes = models.JSONField(
        default=list,
        blank=True,
        help_text='Lista de URLs de imágenes adicionales'
    )
    
    # RATING Y RESEÑAS
    rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Calificación promedio del producto (0-5)'
    )
    
    reseñas = models.PositiveIntegerField(
        default=0,
        help_text='Número total de reseñas'
    )
    
    # VISIBILIDAD Y DESTACADO
    es_destacado = models.BooleanField(
        default=False,
        help_text='Indica si el producto está destacado'
    )
    
    es_nuevo = models.BooleanField(
        default=False,
        help_text='Indica si el producto es nuevo'
    )
    
    esta_activo = models.BooleanField(
        default=True,
        help_text='Indica si el producto está activo'
    )
    
    # METADATOS
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización'
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['categoria', 'esta_activo']),
            models.Index(fields=['es_destacado']),
            models.Index(fields=['es_nuevo']),
            models.Index(fields=['-rating']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    def get_precio_final(self):
        """Retorna el precio con oferta si existe, sino el precio normal"""
        return self.precio_oferta if self.precio_oferta else self.precio
    
    def get_imagen_principal_url(self):
        """Retorna la URL de la imagen principal o un placeholder"""
        if self.imagen_principal:
            return self.imagen_principal.url
        
        # Mapeo de imágenes por nombre de producto usando tus archivos
        mapping = {
            'conjunto deportivo': 'conjunto_Deportive.png',
            'deportivo': 'conjunto_Deportive.png',
            'conjunto size': 'conjunto_size.png',
            'size': 'conjunto_size.png',
            'jogger': 'conjunto_jhogger.png',
            'jogger premium': 'conjunto_jhogger.png',
            'vestido': 'vestido_verano.png',
            'vestido verano': 'vestido_verano.png',
            'body': 'conjunto_size.png',
            'body niño': 'conjunto_size.png',
            'conjunto infantil': 'conjunto_Deportive.png',
            'set bebe': 'conjunto_size.png',
            'set bebé': 'conjunto_size.png',
            'set falda': 'vestido_verano.png',
            'body negro': 'conjunto_size.png',
        }
        
        nombre_lower = self.nombre.lower()
        for key, filename in mapping.items():
            if key in nombre_lower:
                return f'/static/img/productos/{filename}'
        
        # Si tiene categoría, buscar por categoría
        if self.categoria:
            cat_mapping = {
                'niños': 'conjunto_Deportive.png',
                'niñas': 'vestido_verano.png',
                'bebés': 'conjunto_size.png',
                'bebes': 'conjunto_size.png',
            }
            cat_lower = self.categoria.nombre.lower()
            for key, filename in cat_mapping.items():
                if key in cat_lower:
                    return f'/static/img/productos/{filename}'
        
        # Imagen por defecto
        return '/static/img/productos/default.jpg'
    
    def tiene_stock(self):
        """Verifica si el producto tiene stock disponible"""
        return self.stock > 0
    
    def necesita_reposicion(self):
        """Verifica si el producto necesita ser repuesto"""
        return self.stock <= self.stock_minimo
    
    def en_oferta(self):
        """Verifica si el producto está en oferta"""
        return self.precio_oferta is not None and self.precio_oferta < self.precio
    
    def get_porcentaje_descuento(self):
        """Calcula el porcentaje de descuento si está en oferta"""
        if self.en_oferta():
            return int(((self.precio - self.precio_oferta) / self.precio) * 100)
        return 0
    
    def reducir_stock(self, cantidad=1):
        """Reduce el stock del producto"""
        if self.stock >= cantidad:
            self.stock -= cantidad
            self.save()
            logger.info(f'Stock reducido: {self.nombre} - {cantidad} unidades')
            return True
        return False
    
    def aumentar_stock(self, cantidad=1):
        """Aumenta el stock del producto"""
        self.stock += cantidad
        self.save()
        logger.info(f'Stock aumentado: {self.nombre} + {cantidad} unidades')


# ============================================================
# 4. MODELO CARRITO
# ============================================================

class Carrito(models.Model):
    """
    Modelo para el carrito de compras de cada usuario
    """
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito',
        help_text='Usuario propietario del carrito'
    )
    
    creado = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación del carrito'
    )
    
    actualizado = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización del carrito'
    )

    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    def get_total(self):
        """Calcula el total del carrito"""
        total = sum(item.subtotal() for item in self.items.all())
        return total
    
    def get_total_items(self):
        """Retorna la cantidad total de items en el carrito"""
        return sum(item.cantidad for item in self.items.all())
    
    def get_items_count(self):
        """Retorna el número de items diferentes en el carrito"""
        return self.items.count()
    
    def esta_vacio(self):
        """Verifica si el carrito está vacío"""
        return self.items.count() == 0
    
    def vaciar(self):
        """Vacía el carrito"""
        self.items.all().delete()
        logger.info(f'Carrito vaciado: {self.usuario.username}')
    
    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"


# ============================================================
# 5. MODELO CARRITO ITEM
# ============================================================

class CarritoItem(models.Model):
    """
    Modelo para items individuales dentro del carrito
    """
    
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='Carrito al que pertenece el item'
    )
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        help_text='Producto en el carrito'
    )
    
    talla = models.CharField(
        max_length=5,
        help_text='Talla seleccionada del producto'
    )
    
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Cantidad del producto'
    )
    
    fecha_agregado = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha en que se agregó al carrito'
    )

    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        unique_together = ['carrito', 'producto', 'talla']
        indexes = [
            models.Index(fields=['carrito', 'producto']),
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} ({self.talla})"

    def subtotal(self):
        """Calcula el subtotal de este item"""
        return self.producto.get_precio_final() * self.cantidad

    def actualizar_cantidad(self, cantidad):
        """Actualiza la cantidad del item"""
        if cantidad > 0:
            if cantidad <= self.producto.stock:
                self.cantidad = cantidad
                self.save()
                logger.info(f'Item actualizado: {self.producto.nombre} - Cantidad: {cantidad}')
                return True
        return False


# ============================================================
# 6. MODELO FAVORITO
# ============================================================

class Favorito(models.Model):
    """
    Modelo para productos favoritos de los usuarios
    """
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoritos',
        help_text='Usuario que marcó el favorito'
    )
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='favoritos',
        help_text='Producto marcado como favorito'
    )
    
    agregado = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha en que se agregó a favoritos'
    )

    class Meta:
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        unique_together = ('usuario', 'producto')
        ordering = ['-agregado']
        indexes = [
            models.Index(fields=['usuario', 'producto']),
            models.Index(fields=['-agregado']),
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre}"


# ============================================================
# 7. SEÑALES PARA AUDITORÍA (Capa 4)
# ============================================================

@receiver(post_save, sender=Producto)
def producto_post_save(sender, instance, created, **kwargs):
    """Registra creación/actualización de productos"""
    if created:
        logger.info(f'Producto creado: {instance.nombre} - ${instance.precio}')
    else:
        logger.info(f'Producto actualizado: {instance.nombre}')

@receiver(post_save, sender=CarritoItem)
def carrito_item_post_save(sender, instance, created, **kwargs):
    """Registra cambios en el carrito"""
    if created:
        logger.info(
            f'Item agregado al carrito: {instance.carrito.usuario.username} - '
            f'{instance.producto.nombre} x {instance.cantidad}'
        )

@receiver(post_delete, sender=CarritoItem)
def carrito_item_post_delete(sender, instance, **kwargs):
    """Registra eliminación de items del carrito"""
    logger.info(
        f'Item eliminado del carrito: {instance.carrito.usuario.username} - '
        f'{instance.producto.nombre}'
    )