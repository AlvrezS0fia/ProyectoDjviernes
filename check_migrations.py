import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcrm.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT * FROM django_migrations WHERE app = "clientes"')
print(cursor.fetchall())
