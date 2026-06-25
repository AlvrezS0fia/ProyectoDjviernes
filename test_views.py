import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcrm.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

User = get_user_model()

# Create a test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@test.com', 'rol': 'admin'}
)
if created:
    user.set_password('testpass123')
    user.save()

client = Client()
client.login(username='testuser', password='testpass123')

# Test authenticated views
response = client.get('/dashboard/')
print('Dashboard:', response.status_code)

response = client.get('/dashboard/admin/')
print('Dashboard admin:', response.status_code)

response = client.get('/clientes/')
print('Clientes list:', response.status_code)

response = client.get('/clientes/nuevo/')
print('Clientes create:', response.status_code)

response = client.get('/actividades/')
print('Actividades:', response.status_code)

response = client.get('/perfil/')
print('Perfil:', response.status_code)

# Cleanup
user.delete()
