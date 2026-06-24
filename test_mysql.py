import pymysql
import mysql.connector # type: ignore
import sys

print("=" * 50)
print("TEST DE CONEXIÓN A MYSQL")
print("=" * 50)

# Configuración
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'clientes',
    'port': 3306
}

# Prueba 1: pymysql
print("\n1. Probando con pymysql...")
try:
    conn = pymysql.connect(**config)
    print("   ✅ CONEXIÓN EXITOSA con pymysql")
    
    # Probar consulta
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   ✅ Versión MySQL: {version[0]}")
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Prueba 2: mysql.connector
print("\n2. Probando con mysql.connector...")
try:
    conn = mysql.connector.connect(**config)
    print("   ✅ CONEXIÓN EXITOSA con mysql.connector")
    
    # Probar consulta
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"   ✅ Versión MySQL: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Prueba 3: Sin especificar database
print("\n3. Probando conexión sin especificar BD...")
try:
    config_no_db = config.copy()
    del config_no_db['database']
    conn = pymysql.connect(**config_no_db)
    print("   ✅ CONEXIÓN EXITOSA al servidor MySQL")
    
    # Listar bases de datos
    with conn.cursor() as cursor:
        cursor.execute("SHOW DATABASES")
        dbs = cursor.fetchall()
        print("   ✅ Bases de datos disponibles:")
        for db in dbs:
            print(f"      - {db[0]}")
            if db[0] == 'clientes':
                print(f"         👉 ¡BASE DE DATOS 'clientes' ENCONTRADA!")
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)