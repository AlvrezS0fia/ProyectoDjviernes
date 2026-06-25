import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcrm.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
user, created = User.objects.get_or_create(
    username='testfinal',
    defaults={'email': 'final@test.com', 'rol': 'admin'}
)
if created:
    user.set_password('testpass123')
    user.save()

client = Client()
client.login(username='testfinal', password='testpass123')

# Test perfil GET
resp = client.get('/perfil/')
print('GET /perfil/:')
print('  Status:', resp.status_code)
ctx = resp.context or {}
print('  Form errors:', ctx.get('form', 'N/A').errors if 'form' in ctx else 'N/A')
if 'form_cliente' in ctx:
    print('  Form cliente errors:', ctx['form_cliente'].errors)
if 'clientes_con_form' in ctx:
    print('  Clientes count:', len(ctx['clientes_con_form']))

# Test POST crear cliente
resp = client.post('/perfil/', {
    'crear_cliente': '1',
    'identificacion': 'ADMIN123',
    'nombre': 'Admin',
    'apellido': 'Test',
    'email': 'admin@test.com',
    'tipo_cliente': 'regular',
    'activo': 'on',
})
print('POST /perfil/ crear cliente:')
print('  Status:', resp.status_code)
ctx = resp.context or {}
if 'form_cliente' in ctx:
    print('  Form cliente errors:', ctx['form_cliente'].errors)
if 'form' in ctx:
    print('  Form errors:', ctx['form'].errors)

# Test carrito GET
resp = client.get('/tienda/carrito/')
print('GET /tienda/carrito/:')
print('  Status:', resp.status_code)

# Test favoritos
resp = client.get('/favoritos/')
print('GET /favoritos/:')
print('  Status:', resp.status_code)

user.delete()
