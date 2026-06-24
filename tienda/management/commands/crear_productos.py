from django.core.management.base import BaseCommand
from tienda.models import Categoria, Producto

def crear_productos():
    categorias = {
        'niño': Categoria.objects.get_or_create(nombre='Niño', slug='nino')[0],
        'niña': Categoria.objects.get_or_create(nombre='Niña', slug='nina')[0],
        'bebé': Categoria.objects.get_or_create(nombre='Bebé', slug='bebe')[0],
    }
    
    productos_data = [
        {
            'nombre': 'Conjunto Deportivo',
            'categoria': categorias['niño'],
            'subcategoria': 'Deportivo',
            'precio': 899900,
            'descripcion': 'Conjunto deportivo cómodo para niños, perfecto para actividades al aire libre.',
            'tallas': ['2', '4', '6', '8', '10'],
            'stock': 15,
            'rating': 4.5,
        },
        {
            'nombre': 'Jogger Premium',
            'categoria': categorias['niño'],
            'subcategoria': 'Casual',
            'precio': 749900,
            'descripcion': 'Jogger de algodón premium con diseño moderno.',
            'tallas': ['3', '5', '7', '9'],
            'stock': 8,
            'rating': 4.7,
        },
        {
            'nombre': 'Vestido Verano',
            'categoria': categorias['niña'],
            'subcategoria': 'Verano',
            'precio': 699900,
            'descripcion': 'Vestido ligero de verano con estampado floral.',
            'tallas': ['2', '4', '6', '8'],
            'stock': 20,
            'rating': 4.3,
        },
        {
            'nombre': 'Body Bebé',
            'categoria': categorias['bebé'],
            'subcategoria': 'Bodys',
            'precio': 299900,
            'descripcion': 'Body suave para bebé con cierre de madera.',
            'tallas': ['0-3M', '3-6M', '6-12M'],
            'stock': 25,
            'rating': 4.8,
        },
    ]
    
    for p_data in productos_data:
        Producto.objects.get_or_create(
            nombre=p_data['nombre'],
            defaults=p_data
        )

class Command(BaseCommand):
    help = 'Crea productos de muestra'

    def handle(self, *args, **options):
        crear_productos()
        self.stdout.write(self.style.SUCCESS('Productos creados exitosamente'))