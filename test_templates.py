import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcrm.settings')
django.setup()

from django.template import engines

django_engine = engines['django']
template_names = [
    'website/home.html',
    'website/login.html',
    'website/register.html',
    'website/dashboard_admin.html',
    'website/dashboard_user.html',
    'website/favorites.html',
    'website/perfil.html',
    'website/actividades.html',
    'website/gestion_clientes.html',
    'clientes/cliente_form.html',
    'clientes/cliente_confirm_delete.html',
    'clientes/cliente_list.html',
    'clientes/cliente_detail.html',
    'clientes/cliente_import.html',
    'tienda/lista_productos.html',
    'tienda/detalle_producto.html',
    'tienda/carrito.html',
    'tienda/favoritos.html',
]

for name in template_names:
    try:
        django_engine.get_template(name)
        print(f'OK: {name}')
    except Exception as e:
        print(f'ERROR: {name} -> {e}')
