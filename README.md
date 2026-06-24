# 🧸 ANGELOW - CRM & Tienda Online de Ropa Infantil

[![Django](https://img.shields.io/badge/Django-4.2.11-043c2f)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com/)

**ANGELOW** es una aplicación web desarrollada con **Django 4.2.11** que combina un sistema CRM (Customer Relationship Management) con una tienda online para una marca de ropa infantil con sede en Medellín, Colombia.

## 🚀 Características Principales

- ✅ **Autenticación segura** - Registro, Login, Logout con validaciones anti-inyección
- ✅ **Dashboard diferenciado** - Vistas exclusivas para administradores y usuarios regulares
- ✅ **CRM de Clientes** - CRUD completo con autenticación requerida (`/clientes/`)
- ✅ **Catálogo de productos** - Filtros por categoría, búsqueda y detalle de producto
- ✅ **Carrito de compras** - Gestión de cantidades, tallas y items
- ✅ **Favoritos** - Lista de productos favoritos por usuario
- ✅ **API JSON** - Endpoints para integración frontend SPA
- ✅ **Panel de administración** - Django Admin tematizado para gestión del negocio
- ✅ **Responsive** - Interfaz adaptable con Bootstrap 5.3 y Font Awesome

## 📁 Estructura del Proyecto

```
ProyectoDjviernes/
├── dcrm/                              # Configuración del proyecto Django
│   ├── __init__.py
│   ├── settings.py                    # Configuración global (SECRET_KEY, DB, etc.)
│   ├── urls.py                        # Rutas principales
│   ├── wsgi.py                        # WSGI application
│   └── asgi.py                        # ASGI application
│
├── website/                           #  App: Autenticación y Dashboard
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                       # RegisterForm con validaciones personalizadas
│   ├── models.py                      # Usuario (AbstractUser), PerfilUsuario
│   ├── urls.py                        # /accounts/
│   ├── utils.py                       # Validaciones con regex (no_dangerous_chars, valid_name)
│   ├── views.py                       # Login, Register, Logout, Dashboard, Favorites
│   ├── middleware.py                  # SessionSecurityMiddleware
│   └── templates/website/
│       ├── base.html                  # Plantilla base (navbar, footer, css/js)
│       ├── partials/
│       │   ├── navbar.html            # Barra de navegación responsiva
│       │   ├── footer.html            # Pie de página
│       │   └── pagination.html         # Componente de paginación
│       ├── home.html                  # Dashboard principal
│       ├── login.html                 # Inicio de sesión
│       ├── register.html              # Registro de usuarios
│       ├── dashboard_admin.html       # Dashboard para Administradores
│       ├── dashboard_user.html        # Dashboard para Usuarios Regulares
│       └── favorites.html             # Página de favoritos
│
├── clientes/                          #  App: CRM (Customer Relationship Management)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                       # ClienteForm
│   ├── models.py                      # Cliente
│   ├── urls.py                        # /clientes/
│   ├── views.py                       # CRUD completo de clientes
│   └── templates/clientes/
│       ├── cliente_list.html          # Lista de clientes
│       ├── cliente_form.html          # Crear/Editar cliente
│       └── cliente_confirm_delete.html # Confirmar eliminación
│
├── tienda/                            # 🅲 App: Tienda Online
│   ├── __init__.py
│   ├── admin.py                       # Configuración del admin para productos
│   ├── apps.py
│   ├── forms.py                       # Formularios para carrito y favoritos
│   ├── models.py                      # Categoria, Producto, Carrito, CarritoItem, Favorito
│   ├── urls.py                        # / (tienda) + /api/
│   ├── views.py                       # Productos, Carrito, Favoritos, API
│   └── templates/tienda/
│       ├── lista_productos.html       # Catálogo de productos
│       ├── detalle_producto.html      # Detalle del producto
│       ├── carrito.html               # Carrito de compras
│       └── favoritos.html             # Lista de favoritos (server-side)
│
├── manage.py                          # Script de gestión de Django
├── requirements.txt                   # Dependencias del proyecto
├── .env                               # Variables de entorno (opcional)
├── diagramas.puml                     # Diagramas UML (PlantUML)
│
├── static/                            # Archivos estáticos globales
│   ├── css/
│   │   ├── style.css                  # Estilos personalizados principales
│   │   ├── tienda.css                 # Estilos específicos de la tienda
│   │   ├── bootstrap.min.css          # Bootstrap 5.3 (local)
│   │   └── fontawesome.min.css        # Font Awesome (local)
│   ├── js/
│   │   ├── main.js                    # Scripts principales (SPA, funcionalidades)
│   │   ├── bootstrap.bundle.min.js   # Bootstrap JS (local)
│   │   └── fontawesome.min.js         # Font Awesome JS (local)
│   └── img/
│       ├── logo.png                   # Logo de ANGELOW
│       ├── favico.ico                 # Favicon
│       ├── default-product.jpg        # Imagen placeholder
│       └── productos/                 # Imágenes de productos (estáticas)
│
├── media/                             # Archivos subidos dinámicamente
│   └── productos/                     # Imágenes de productos cargadas por admin
│
└── templates/                         # Templates globales del sistema
    └── admin/
        └── base_site.html             # Plantilla personalizada del admin
```

## 🗄️ Modelos de Base de Datos

### Tienda App

| Modelo | Campos principales |
|--------|-------------------|
| **Categoria** | nombre, slug, descripción, imagen |
| **Producto** | nombre, slug, categoría, precio, descripción, tallas (JSON), stock, rating, activo |
| **Carrito** | usuario (FK), fecha_creacion |
| **CarritoItem** | carrito (FK), producto (FK), talla, cantidad |
| **Favorito** | usuario (FK), producto (FK), fecha_agregado |

### Clientes App

| Modelo | Campos |
|--------|--------|
| **Cliente** | nombre, email (único), telefono, direccion, fecha_registro |

### Website App

| Modelo | Descripción |
|--------|-------------|
| **Usuario** | Extiende AbstractUser con email como username |

## 🔌 API Endpoints (JSON)

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/productos/` | GET | Lista de productos disponibles | ❌ |
| `/api/carrito/` | GET | Datos del carrito del usuario | ✅ |
| `/api/carrito/agregar/` | POST | Agregar producto al carrito | ✅ |
| `/api/favoritos/toggle/` | POST | Alternar favorito | ✅ |

### Ejemplo Respuesta API Productos

```json
{
  "products": [
    {
      "id": 1,
      "name": "Conjunto Deportivo",
      "category": "Niño",
      "subcategory": "Conjuntos",
      "price": 899900,
      "description": "Conjunto deportivo cómodo",
      "sizes": ["4", "6", "8"],
      "imgs": ["/static/img/productos/conjunto_size.png"],
      "stock": 12,
      "rating": 4.5,
      "reviews": 0
    }
  ]
}
```

## 🛣️ Rutas Principales

| Ruta | Vista | Descripción |
|------|-------|-------------|
| `/` | `tienda:lista_productos` | Catálogo de productos |
| `/producto/<slug>/` | `tienda:detalle_producto` | Detalle de producto |
| `/carrito/` | `tienda:ver_carrito` | Ver carrito de compras |
| `/carrito/agregar/<id>/` | `tienda:agregar_al_carrito` | Agregar al carrito |
| `/carrito/actualizar/<id>/` | `tienda:actualizar_carrito` | Actualizar cantidad |
| `/carrito/eliminar/<id>/` | `tienda:eliminar_del_carrito` | Eliminar item |
| `/favoritos/` | `tienda:favoritos` | Mis favoritos |
| `/api/productos/` | `tienda:api_productos` | JSON productos |
| `/accounts/` | `website:home` | Dashboard principal |
| `/accounts/login/` | `website:login_view` | Iniciar sesión |
| `/accounts/register/` | `website:register_view` | Registrarse |
| `/accounts/logout/` | `website:logout_view` | Cerrar sesión |
| `/clientes/` | `clientes:cliente_list` | Lista de clientes |
| `/clientes/nuevo/` | `clientes:cliente_create` | Crear cliente |
| `/clientes/editar/<id>/` | `clientes:cliente_update` | Editar cliente |
| `/clientes/eliminar/<id>/` | `clientes:cliente_delete` | Eliminar cliente |

## 🛠️ Instalación y Configuración

### Requisitos previos

- Python 3.10 o superior
- pip (incluido con Python)
- Git (opcional, para clonar)

### Instalación completa

```bash
# 1. Clonar el repositorio (si aplica)
git clone <url-del-repo>
cd ProyectoDjviernes

# 2. Activar entorno virtual (Windows)
.\entorno\Scripts\activate
# Linux/Mac:
# source entorno/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones (SQLite por defecto)
python manage.py migrate

# 5. Crear superusuario para el panel admin
python manage.py createsuperuser

# 6. Ejecutar servidor de desarrollo
python manage.py runserver
```

### Acceder a la aplicación

- **Tienda (público):** http://localhost:8000/
- **Admin Django:** http://localhost:8000/admin/
- **Cuentas:** http://localhost:8000/accounts/login/
- **CRM Clientes:** http://localhost:8000/clientes/ (requiere login)

## ⚙️ Configuración

### Variables de entorno (`.env`)

El proyecto soporta variables de entorno via `python-dotenv`. Crear `.env` en la raíz:

```env
# Django
SECRET_KEY=tu-clave-secreta-super-segura-aqui-generada-con-secrets-module
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (SQLite por defecto)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Para MySQL en producción (descomentar y configurar):
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=nombre_base_datos
# DB_USER=usuario_mysql
# DB_PASSWORD=contraseña_mysql
# DB_HOST=localhost
# DB_PORT=3306

# Email (consola en desarrollo)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Base de datos

El proyecto viene configurado con **SQLite3** por defecto. Para migrar a **MySQL**:

1. Instalar PyMySQL: `pip install PyMySQL`
2. Configurar las variables de entorno de MySQL en `.env`
3. Ejecutar migraciones: `python manage.py migrate`

## 🔒 Seguridad

La aplicación incluye configuraciones de seguridad robustas:

- 🛡️ CSRF protection activada en todos los formularios
- 🍪 Cookies seguras (`HttpOnly`, `SameSite=Lax`)
- 🔐 Validación de contraseñas robusta (mínimo 8 caracteres, mayúsculas, minúsculas, caracteres especiales)
- 🚦 Limitador de intentos de login (máx. 5 intentos por IP, bloqueo de 15 min)
- ⏱️ Sesión con expiración de 1 hora de inactividad
- 🧹 Limpieza de caracteres peligrosos (anti-SQLi, anti-XSS, anti-CRLF)
- 🔒 Session Security Middleware para detección de hijacking

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Con verbosidad
python manage.py test -v 2
```

## 🎨 Frontend

### Arquitectura

- **Plantilla base:** `templates/website/base.html` - Incluye navbar, footer, messages
- **CSS Framework:** Bootstrap 5.3 (archivos locales en `static/css/`)
- **Iconos:** Font Awesome 6.5 (archivos locales en `static/css/` y `static/js/`)
- **JavaScript:** `static/js/main.js` para funcionalidades SPA
- **Imágenes:** Productos estáticos en `static/img/productos/`, uploads en `media/productos/`

### Estructura de templates

- **Base:** `website/templates/website/base.html` - Template padre con navbar y footer
- **Auth:** `login.html`, `register.html` - Vistas públicas
- **Dashboard:** `home.html` (SPA), `dashboard_admin.html`, `dashboard_user.html`
- **Tienda:** `tienda/templates/tienda/*.html` - Templates específicos de la app tienda
- **CRM:** `clientes/templates/clientes/*.html` - Templates específicos de clientes

## Dar de alta productos

Para agregar productos al catálogo:

1. Acceder al panel de administración: http://localhost:8000/admin/
2. Ir a **Tienda > Productos** y crear un nuevo producto
3. Subir las imágenes del producto (se guardan en `media/productos/`)
4. Configurar categoría, precio, stock, tallas en formato JSON (ej: `["4", "6", "8"]`)

## 📊 Diagramas UML

El archivo `diagramas.puml` contiene los diagramas PlantUML de:
- Diagrama de Entidad-Relación (ERD)
- Diagrama de Casos de Uso
- Diagrama de Clases (si aplica)

Para visualizar: https://www.plantuml.com/plantuml

## 🚀 Despliegue a Producción

1. **Configurar `DEBUG = False`** en `settings.py`
2. **Configurar `ALLOWED_HOSTS`** con el dominio real
3. **Migrar a MySQL:**
   - Configurar variables de entorno con datos de MySQL
   - Ejecutar `python manage.py migrate`
4. **Configurar SSL:**
   - `SECURE_SSL_REDIRECT = True`
   - Agregar dominio a `CSRF_TRUSTED_ORIGINS`
5. **Recolectar archivos estáticos:**
   - `python manage.py collectstatic`
6. **Usar servidor WSGI** como Gunicorn/uWSGI detrás de Nginx

## 🏗️ Arquitectura y Decisiones Técnicas

- **Patrón MTV** (Model-Template-View) de Django
- **SPA ligera** en la página home con JavaScript vanilla
- **API JSON** para desacoplar frontend de backend
- **Validación server-side** estricta en forms y utils
- **Organización por apps** con templates y staticfiles aislados
- **Localización** en español colombiano (`es-co`, `America/Bogota`)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Proyecto privado - ANGELOW Colombia  
© 2024 ANGELOW. Todos los derechos reservados.

---
Desarrollado con ❤️ para ANGELOW - Ropa Infantil en Medellín, Colombia
