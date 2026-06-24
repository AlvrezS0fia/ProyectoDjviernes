# tienda/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Categoria, Producto, Carrito, CarritoItem, Favorito

# Obtener el modelo de usuario personalizado
Usuario = get_user_model()

# ============================================================
# REGISTRAR EL MODELO USUARIO EN EL ADMIN (Si no está registrado)
# ============================================================

# Verificar si el modelo Usuario ya está registrado
if not admin.site.is_registered(Usuario):
    from django.contrib.auth.admin import UserAdmin
    
    @admin.register(Usuario)
    class UsuarioAdmin(UserAdmin):
        list_display = ['username', 'email', 'rol', 'first_name', 'last_name', 'is_active']
        list_filter = ['rol', 'is_active']
        search_fields = ['username', 'email', 'first_name', 'last_name']
        fieldsets = UserAdmin.fieldsets + (
            ('Información Adicional', {
                'fields': ('rol', 'telefono', 'direccion', 'fecha_nacimiento')
            }),
        )
        add_fieldsets = UserAdmin.add_fieldsets + (
            ('Información Adicional', {
                'fields': ('rol', 'telefono', 'direccion', 'fecha_nacimiento')
            }),
        )

# ============================================================
# ADMIN DE CATEGORÍAS
# ============================================================

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'icono', 'es_activa', 'orden', 'fecha_creacion']
    list_filter = ['es_activa']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['orden', 'es_activa']
    list_per_page = 25


# ============================================================
# ADMIN DE PRODUCTOS
# ============================================================

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'categoria', 
        'precio', 
        'precio_oferta',
        'stock', 
        'es_destacado',
        'esta_activo',
        'rating',
        'fecha_creacion'
    ]
    list_filter = ['categoria', 'es_destacado', 'esta_activo', 'stock']
    search_fields = ['nombre', 'descripcion', 'subcategoria']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['precio', 'precio_oferta', 'stock', 'es_destacado', 'esta_activo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'categoria', 'subcategoria')
        }),
        ('Precios y Stock', {
            'fields': ('precio', 'precio_oferta', 'stock', 'stock_minimo')
        }),
        ('Descripción y Detalles', {
            'fields': ('descripcion', 'caracteristicas', 'tallas')
        }),
        ('Imágenes', {
            'fields': ('imagen_principal', 'imagenes')
        }),
        ('Rating y Visibilidad', {
            'fields': ('rating', 'reseñas', 'es_destacado', 'es_nuevo', 'esta_activo')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


# ============================================================
# ADMIN DE CARRITO
# ============================================================

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'creado', 'actualizado', 'get_total', 'get_total_items']
    list_filter = ['creado', 'actualizado']
    search_fields = ['usuario__username', 'usuario__email']
    readonly_fields = ['creado', 'actualizado']
    raw_id_fields = ['usuario']  # <--- Usar raw_id_fields

    def get_total(self, obj):
        return f"${obj.get_total():,.0f}"
    get_total.short_description = 'Total'

    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Items'


@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ['carrito', 'producto', 'talla', 'cantidad', 'subtotal']
    list_filter = ['talla', 'fecha_agregado']
    search_fields = ['producto__nombre', 'carrito__usuario__username']
    raw_id_fields = ['carrito', 'producto']  # <--- Usar raw_id_fields
    readonly_fields = ['fecha_agregado']

    def subtotal(self, obj):
        return f"${obj.subtotal():,.0f}"
    subtotal.short_description = 'Subtotal'


# ============================================================
# ADMIN DE FAVORITOS - CORREGIDO
# ============================================================

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'agregado']
    list_filter = ['agregado']
    search_fields = ['usuario__username', 'usuario__email', 'producto__nombre']
    raw_id_fields = ['usuario', 'producto']  # <--- Usar raw_id_fields en lugar de autocomplete_fields
    readonly_fields = ['agregado']
    list_per_page = 25
    
    # ELIMINADO: autocomplete_fields = ['usuario']  # <--- Esto causaba el error
    