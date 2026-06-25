import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcrm.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()
cursor.execute("PRAGMA table_info(clientes_cliente)")
print(cursor.fetchall())
