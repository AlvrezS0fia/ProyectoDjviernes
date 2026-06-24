from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categorías"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    subcategoria = models.CharField(max_length=100, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    descripcion = models.TextField()
    tallas = models.JSONField(default=list, help_text="Lista de tallas disponibles")
    imagen_principal = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagenes = models.JSONField(default=list, help_text="Lista de URLs de imágenes adicionales")
    stock = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=4.5)
    reseñas = models.PositiveIntegerField(default=0)
    caracteristicas = models.JSONField(default=list)

    class Meta:
        verbose_name_plural = "Productos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_imagen_principal_url(self):
        if self.imagen_principal:
            return self.imagen_principal.url
        mapping = {
            'Conjunto Deportivo': '/static/images/productos/conjunto_Deportive.png',
            'Jogger Premium': '/static/images/productos/conjunto_jhogger.png',
            'Vestido Verano': '/static/images/productos/vestido_verano.png',
            'Body Bebé': '/static/images/productos/conjunto_size.png',
            'Set Bebé': '/static/images/productos/conjunto_size.png',
        }
        for key, url in mapping.items():
            if key.lower() in self.nombre.lower() or self.nombre.lower() in key.lower():
                return url
        return '/static/images/placeholder.png'

    def __str__(self):
        return self.nombre

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    creado = models.DateTimeField(auto_now_add=True)

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    talla = models.CharField(max_length=5)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad

class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')