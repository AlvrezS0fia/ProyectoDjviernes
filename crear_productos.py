# crear_productos.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcrm.settings')
django.setup()

from tienda.models import Producto, Categoria

# ============================================================
# CATEGORÍAS
# ============================================================
categorias_data = [
    {'nombre': 'Bebés', 'slug': 'bebes'},
    {'nombre': 'Niños', 'slug': 'ninos'},
    {'nombre': 'Niñas', 'slug': 'ninas'},
    {'nombre': 'Edición Especial', 'slug': 'edicion-especial'},
]

# ============================================================
# PRODUCTOS
# ============================================================
productos_data = [
    {
        'nombre': 'Conjunto Bebé Invierno',
        'slug': 'conjunto-bebe-invierno',
        'categoria': 'bebes',
        'subcategoria': 'Ropa de invierno',
        'descripcion': 'Conjunto abrigado para bebé con diseño exclusivo. Incluye chaqueta, pantalón y gorro. Ideal para los días fríos.',
        'precio': 49900,
        'precio_oferta': 39900,
        'stock': 15,
        'tallas': '2,4,6,8',
        'es_destacado': True
    },
    {
        'nombre': 'Vestido Verano Niña',
        'slug': 'vestido-verano-nina',
        'categoria': 'ninas',
        'subcategoria': 'Vestidos',
        'descripcion': 'Vestido floral de verano para niña. Fresco, cómodo y perfecto para días soleados. Diseño con volantes.',
        'precio': 35900,
        'precio_oferta': None,
        'stock': 20,
        'tallas': '4,6,8,10',
        'es_destacado': False
    },
    {
        'nombre': 'Camiseta Niño',
        'slug': 'camiseta-nino',
        'categoria': 'ninos',
        'subcategoria': 'Ropa casual',
        'descripcion': 'Camiseta de algodón 100% para niño. Diseño divertido con estampado de dinosaurios. Muy resistente y cómoda.',
        'precio': 28900,
        'precio_oferta': 22900,
        'stock': 25,
        'tallas': 'S,M,L,XL',
        'es_destacado': False
    },
    {
        'nombre': 'Body Bebé Algodón',
        'slug': 'body-bebe-algodon',
        'categoria': 'bebes',
        'subcategoria': 'Bodys',
        'descripcion': 'Body de algodón orgánico para bebé. Suave, transpirable y cómodo. Cierre de presión para fácil cambio.',
        'precio': 19900,
        'precio_oferta': None,
        'stock': 30,
        'tallas': '0-3,3-6,6-9,9-12',
        'es_destacado': True
    },
    {
        'nombre': 'Pijama Niña Unicornio',
        'slug': 'pijama-nina-unicornio',
        'categoria': 'ninas',
        'subcategoria': 'Pijamas',
        'descripcion': 'Pijama de invierno para niña con diseño de unicornio. Muy cálida, suave y con detalles brillantes.',
        'precio': 42900,
        'precio_oferta': 37900,
        'stock': 12,
        'tallas': '4,6,8,10',
        'es_destacado': False
    },
    {
        'nombre': 'Conjunto Deportivo Niño',
        'slug': 'conjunto-deportivo-nino',
        'categoria': 'ninos',
        'subcategoria': 'Conjuntos',
        'descripcion': 'Conjunto deportivo para niño. Incluye sudadera con capucha y pantaloneta. Perfecto para jugar y hacer deporte.',
        'precio': 55900,
        'precio_oferta': 45900,
        'stock': 18,
        'tallas': 'S,M,L',
        'es_destacado': False
    },
    {
        'nombre': 'Chaqueta Bebé',
        'slug': 'chaqueta-bebe',
        'categoria': 'bebes',
        'subcategoria': 'Chaqueta',
        'descripcion': 'Chaqueta acolchada para bebé. Muy abrigada, con capucha y cierre de cremallera. Ideal para paseos.',
        'precio': 68900,
        'precio_oferta': 58900,
        'stock': 10,
        'tallas': '6,9,12',
        'es_destacado': False
    },
    {
        'nombre': 'Falda Niña',
        'slug': 'falda-nina',
        'categoria': 'ninas',
        'subcategoria': 'Faldas',
        'descripcion': 'Falda de tul para niña. Diseño elegante con capas, perfecta para ocasiones especiales y eventos.',
        'precio': 45900,
        'precio_oferta': None,
        'stock': 15,
        'tallas': '4,6,8',
        'es_destacado': False
    },
    {
        'nombre': 'Pantalón Niño',
        'slug': 'pantalon-nino',
        'categoria': 'ninos',
        'subcategoria': 'Pantalones',
        'descripcion': 'Pantalón cargo para niño. Resistente, cómodo y con múltiples bolsillos. Perfecto para la escuela.',
        'precio': 38900,
        'precio_oferta': 32900,
        'stock': 22,
        'tallas': 'S,M,L,XL',
        'es_destacado': False
    },
    {
        'nombre': 'Conjunto Bebé Verano',
        'slug': 'conjunto-bebe-verano',
        'categoria': 'bebes',
        'subcategoria': 'Ropa de verano',
        'descripcion': 'Conjunto de verano para bebé. Incluye body manga corta y pantalón corto. Fresco y cómodo.',
        'precio': 29900,
        'precio_oferta': 24900,
        'stock': 25,
        'tallas': '2,4,6,8',
        'es_destacado': False
    },
]

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def crear_productos():
    print("=" * 50)
    print("🚀 CREANDO CATEGORÍAS Y PRODUCTOS")
    print("=" * 50)
    
    # Crear categorías
    print("\n📁 Creando categorías...")
    categorias = {}
    for cat in categorias_data:
        categoria, created = Categoria.objects.get_or_create(
            slug=cat['slug'],
            defaults={
                'nombre': cat['nombre'],
                'es_activa': True
            }
        )
        categorias[cat['slug']] = categoria
        estado = "✨ creada" if created else "📌 existente"
        print(f"  ✅ {categoria.nombre} - {estado}")
    
    # Crear productos
    print("\n📦 Creando productos...")
    for prod in productos_data:
        categoria = categorias.get(prod['categoria'])
        if not categoria:
            print(f"  ❌ Categoría '{prod['categoria']}' no encontrada para {prod['nombre']}")
            continue
        
        producto, created = Producto.objects.get_or_create(
            slug=prod['slug'],
            defaults={
                'nombre': prod['nombre'],
                'categoria': categoria,
                'subcategoria': prod['subcategoria'],
                'descripcion': prod['descripcion'],
                'precio': prod['precio'],
                'precio_oferta': prod['precio_oferta'],
                'stock': prod['stock'],
                'tallas': prod['tallas'],
                'esta_activo': True,
                'es_destacado': prod.get('es_destacado', False)
            }
        )
        estado = "✨ creado" if created else "📌 existente"
        print(f"  ✅ {producto.nombre} - ${producto.precio:,} - {estado}")
    
    # Resumen
    total_categorias = Categoria.objects.count()
    total_productos = Producto.objects.count()
    print("\n" + "=" * 50)
    print(f"🎉 ¡PRODUCTOS CREADOS EXITOSAMENTE!")
    print(f"📊 Total categorías: {total_categorias}")
    print(f"📊 Total productos: {total_productos}")
    print("=" * 50)

if __name__ == "__main__":
    crear_productos()