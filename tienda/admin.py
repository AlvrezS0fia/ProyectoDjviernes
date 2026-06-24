from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto, Carrito, CarritoItem, Favorito

# ==================== INLINE ====================
class CarritoItemInline(admin.TabularInline):
    model = CarritoItem
    extra = 0
    fields = ('producto', 'talla', 'cantidad', 'subtotal_display')
    readonly_fields = ('subtotal_display',)
    autocomplete_fields = ('producto',)
    show_change_link = True

    def subtotal_display(self, obj):
        if obj.pk:
            return f"${obj.subtotal():,.0f} COP"
        return "—"
    subtotal_display.short_description = 'Subtotal'

# ==================== CATEGORÍA ====================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'cantidad_productos', 'creada')
    search_fields = ('nombre', 'slug')
    ordering = ('nombre',)
    list_per_page = 30

    fieldsets = (
        ('Información básica', {
            'fields': ('nombre',),
            'description': 'El slug se genera automáticamente desde el nombre.'
        }),
    )
    readonly_fields = ('slug',)

    def cantidad_productos(self, obj):
        return obj.productos.count()
    cantidad_productos.short_description = 'Productos'
    cantidad_productos.admin_order_field = 'nombre'

    def creada(self, obj):
        return obj.pk is not None
    creada.short_description = 'Estado'
    creada.boolean = True

# ==================== PRODUCTO ====================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'subcategoria', 'precio', 'stock', 'precio_formateado', 'stock_badge', 'rating', 'reseñas')
    list_filter = ('categoria', 'subcategoria', 'stock')
    search_fields = ('nombre', 'descripcion', 'subcategoria', 'categoria__nombre')
    ordering = ('-id',)
    list_editable = ('precio', 'stock', 'subcategoria')
    list_per_page = 25

    fieldsets = (
        ('Información del producto', {
            'fields': ('categoria', 'subcategoria', 'nombre'),
            'description': 'Datos básicos del producto. El slug se genera automáticamente.'
        }),
        ('Imagen', {
            'fields': ('imagen_principal', 'imagenes'),
            'description': 'Imagen principal del producto y galería adicional (URLs).'
        }),
        ('Contenido', {
            'fields': ('descripcion', 'caracteristicas'),
            'description': 'Descripción detallada y lista de características del producto.'
        }),
        ('Precio e inventario', {
            'fields': ('precio', 'stock', 'tallas'),
            'description': 'Precio en COP, cantidad disponible y tallas ofrecidas.'
        }),
        ('Valoración', {
            'fields': ('rating', 'reseñas'),
            'classes': ('collapse',),
            'description': 'Datos de calificación calculados automáticamente.'
        }),
    )
    readonly_fields = ('slug',)

    actions = ['aumentar_precio_10', 'aumentar_precio_15', 'restablecer_stock', 'marcar_sin_stock']

    def precio_formateado(self, obj):
        return f"${obj.precio:,.0f} COP"
    precio_formateado.short_description = 'Precio (formateado)'
    precio_formateado.admin_order_field = 'precio'

    def stock_badge(self, obj):
        if obj.stock == 0:
            return format_html('<span class="stock-badge-low" style="color:#dc3545; font-weight:bold;">Agotado</span>')
        elif obj.stock < 10:
            return format_html('<span class="stock-badge-low" style="color:#fd7e14; font-weight:bold;">Bajo ({})</span>', obj.stock)
        elif obj.stock < 30:
            return format_html('<span class="stock-badge-mid" style="color:#ffc107; font-weight:bold;">Medio ({})</span>', obj.stock)
        else:
            return format_html('<span class="stock-badge-ok" style="color:#28a745; font-weight:bold;">Disponible ({})</span>', obj.stock)
    stock_badge.short_description = 'Stock'
    stock_badge.admin_order_field = 'stock'

    def aumentar_precio_10(self, request, queryset):
        for p in queryset:
            p.precio = float(p.precio) * 1.10
            p.save(update_fields=['precio'])
        self.message_user(request, f"Precio aumentado un 10% en {queryset.count()} productos.")
    aumentar_precio_10.short_description = "Aumentar precio 10%"

    def aumentar_precio_15(self, request, queryset):
        for p in queryset:
            p.precio = float(p.precio) * 1.15
            p.save(update_fields=['precio'])
        self.message_user(request, f"Precio aumentado un 15% en {queryset.count()} productos.")
    aumentar_precio_15.short_description = "Aumentar precio 15%"

    def restablecer_stock(self, request, queryset):
        count = queryset.update(stock=0)
        self.message_user(request, f"Stock restablecido a 0 en {count} productos. Recuerda actualizar el inventario.")
    restablecer_stock.short_description = "Restablecer stock (marcar agotado)"

    def marcar_sin_stock(self, request, queryset):
        count = queryset.filter(stock=0).count()
        self.message_user(request, f"{count} producto(s) sin stock disponible.", level='warning')
    marcar_sin_stock.short_description = "Ver productos sin stock"

# ==================== CARRITO ====================
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'email_usuario', 'total_items', 'total_valor', 'creado')
    search_fields = ('usuario__username', 'usuario__email', 'usuario__first_name', 'usuario__last_name')
    list_filter = ('creado',)
    inlines = [CarritoItemInline]
    ordering = ('-creado',)
    date_hierarchy = 'creado'
    list_per_page = 20

    readonly_fields = ('total_items', 'total_valor', 'creado')
    fields = ('usuario',)

    def email_usuario(self, obj):
        return obj.usuario.email
    email_usuario.short_description = 'Email'
    email_usuario.admin_order_field = 'usuario__email'

    def total_items(self, obj):
        return sum(item.cantidad for item in obj.items.all())
    total_items.short_description = 'Items'

    def total_valor(self, obj):
        total = sum(item.subtotal() for item in obj.items.all())
        return f"${total:,.0f} COP"
    total_valor.short_description = 'Valor total'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario').prefetch_related('items')

# ==================== CARRITO ITEM ====================
@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'carrito', 'producto', 'talla', 'cantidad', 'subtotal_columna')
    list_filter = ('talla',)
    search_fields = ('producto__nombre', 'carrito__usuario__username')
    ordering = ('-id',)
    list_per_page = 30
    autocomplete_fields = ('carrito', 'producto')

    fieldsets = (
        ('Relaciones', {
            'fields': ('carrito', 'producto'),
        }),
        ('Detalles del item', {
            'fields': ('talla', 'cantidad'),
            'description': 'Talla seleccionada y cantidad del producto.'
        }),
    )

    def subtotal_columna(self, obj):
        return f"${obj.subtotal():,.0f} COP"
    subtotal_columna.short_description = 'Subtotal'
    subtotal_columna.admin_order_field = 'producto__precio'

# ==================== FAVORITO ====================
@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'categoria', 'precio_producto', 'agregado')
    list_filter = ('agregado', 'producto__categoria')
    search_fields = ('usuario__username', 'usuario__email', 'producto__nombre', 'producto__categoria__nombre')
    ordering = ('-agregado',)
    list_per_page = 25
    date_hierarchy = 'agregado'
    autocomplete_fields = ('usuario', 'producto')
    readonly_fields = ('agregado',)

    fieldsets = (
        ('Relaciones', {
            'fields': ('usuario', 'producto'),
            'description': 'Usuario que marcó el producto como favorito.'
        }),
        ('Información del sistema', {
            'fields': ('agregado',),
            'classes': ('collapse',),
            'description': 'Fecha en que se agregó a favoritos.'
        }),
    )

    def categoria(self, obj):
        return obj.producto.categoria.nombre
    categoria.short_description = 'Categoría'
    categoria.admin_order_field = 'producto__categoria__nombre'

    def precio_producto(self, obj):
        return f"${obj.producto.precio:,.0f} COP"
    precio_producto.short_description = 'Precio'
    precio_producto.admin_order_field = 'producto__precio'