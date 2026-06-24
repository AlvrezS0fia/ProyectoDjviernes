# 🧸 ANGELOW - CRM & Tienda Online de Ropa Infantil

[![Django](https://img.shields.io/badge/Django-4.2.11-043c2f)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com/)

**ANGELOW** es una aplicación web desarrollada con **Django 4.2.11** que combina un sistema CRM (Customer Relationship Management) con una tienda online para una marca de ropa infantil con sede en Medellín, Colombia.

---

## 🚀 Características Principales

### 🔐 Autenticación y Seguridad
- ✅ Registro, Login y Logout con validaciones anti-inyección
- ✅ Roles de usuario: `admin`, `vendedor`, `user`
- ✅ Limitador de intentos de login (máx. 5 intentos por IP, bloqueo de 15 min)
- ✅ Sesión con expiración por inactividad (30 min) y tiempo máximo (8 horas)
- ✅ Protección contra fuerza bruta y CSRF en todos los formularios
- ✅ Cookies seguras (`HttpOnly`, `SameSite=Lax`)
- ✅ Middleware de detección de hijacking de sesión (IP y User-Agent)

### 🖥️ Dashboards Diferenciados
- ✅ Panel de administrador con estadísticas completas
- ✅ Panel de usuario regular con favoritos y actividades
- ✅ Redirección automática según rol de usuario

### 👥 CRM de Clientes (App `clientes`)
- ✅ CRUD completo de clientes con autenticación requerida
- ✅ Filtros avanzados: por nombre, email, tipo de cliente, estado, fecha de registro
- ✅ Paginación de resultados (10 clientes por página)
- ✅ Soft delete (eliminación lógica) de clientes
- ✅ Clasificación de clientes: Regular, VIP, Corporativo, Distribuidor
- ✅ Auditoría completa de creación, edición y eliminación
- ✅ Exportación de clientes a CSV (solo admin)
- ✅ Importación de clientes desde CSV (solo admin)
- ✅ API JSON para integración frontend

### 🛍️ Tienda Online (App `tienda`)
- ✅ Catálogo de productos con filtros por categoría (Niños, Niñas, Bebés, Edición especial, Oferta, Popular, Body's, Pijamas, Vestidos, Conjunto)
- ✅ Búsqueda de productos en tiempo real con contador de resultados
- ✅ Detalle de producto con cambio de imagen principal, favoritos y carrito
- ✅ Carrito de compras con gestión de cantidades y tallas
- ✅ Lista de productos favoritos por usuario con persistencia en localStorage
- ✅ Productos destacados en página de inicio
- ✅ Control de stock y activación/desactivación de productos
- ✅ Badges de oferta, nuevo y destacado en tarjetas de producto
- ✅ Comando management para crear productos de prueba (`python manage.py crear_productos`)

### 📊 Panel de Administración
- ✅ Django Admin tematizado para gestión del negocio
- ✅ Gestión de productos, categorías, clientes y usuarios
- ✅ Registro de actividades y auditoría del sistema

### 🎨 Frontend (SPA - Single Page Application)
- ✅ Hero carousel animado con 5 slides (tarjetas de regalo, promociones, envío gratis)
- ✅ Navegación por puntos, botones anterior/siguiente y progress bar
- ✅ Autoplay con pausa al hover y soporte táctil (swipe)
- ✅ Filtro de categorías con pills interactivos
- ✅ Búsqueda en tiempo real con limpieza de filtros
- ✅ Tarjetas de producto con hover effects (elevación, zoom en imagen)
- ✅ Sistema de favoritos con corazón rojo y contador dinámico en el navbar
- ✅ Carrito de compras con badge y persistencia en localStorage
- ✅ Toast notifications animadas para feedback de usuario (éxito, error,warning,info)
- ✅ Interfaz responsive con Bootstrap 5.3 y CSS Grid
- ✅ Iconos con Font Awesome 6.5
- ✅ Diseño adaptado a la marca ANGELOW (ropa infantil)

---

## 📁 Estructura del Proyecto

```
ProyectoDjviernes/
├── dcrm/                              # Configuración del proyecto Django
│   ├── __init__.py
│   ├── settings.py                    # Configuración global (SECRET_KEY, DB, roles, middlewares)
│   ├── urls.py                        # Rutas principales
│   ├── wsgi.py                        # WSGI application
│   └── asgi.py                        # ASGI application
│
├── website/                           # App: Autenticación, Dashboard y Usuarios
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                       # RegisterForm, LoginForm, PerfilUsuarioForm, RecordForm
│   ├── models.py                      # Usuario (AbstractUser), Record, ActividadUsuario
│   ├── urls.py                        # /accounts/
│   ├── utils.py                       # Validaciones con regex
│   ├── views.py                       # Login, Register, Logout, Dashboard, Favorites, Perfil, Actividades
│   ├── middleware.py                  # 5 middlewares personalizados (SessionSecurity, LoginAttempt, ActivityLog, SecurityHeaders, RateLimit)
│   ├── tests.py                       # Tests de la app website
│   └── templates/website/
│       ├── base.html                  # Plantilla base principal (navbar, footer, css/js)
│       ├── base_auth.html             # Plantilla base para páginas de autenticación (login, register)
│       ├── partials/
│       │   ├── navbar.html            # Barra de navegación responsiva con badges de carrito y favoritos
│       │   ├── footer.html            # Pie de página
│       │   └── pagination.html         # Componente de paginación
│       ├── home.html                  # Página principal SPA con hero carousel, categorías, productos y buscador
│       ├── login.html                 # Inicio de sesión
│       ├── register.html              # Registro de usuarios
│       ├── dashboard_admin.html       # Dashboard para Administradores
│       ├── dashboard_user.html        # Dashboard para Usuarios Regulares
│       └── favorites.html             # Página de favoritos completa con CSS y JS integrado
│
├── clientes/                          # App: CRM (Customer Relationship Management)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                       # ClienteForm, ClienteFilterForm, ClienteImportForm
│   ├── models.py                      # Cliente (con validadores, señales y auditoría)
│   ├── urls.py                        # /clientes/
│   ├── views.py                       # CRUD completo, exportar, importar, API clientes
│   ├── tests.py                       # Tests de la app clientes
│   └── templates/clientes/
│       ├── cliente_list.html          # Lista de clientes con filtros
│       ├── cliente_form.html          # Crear/Editar cliente
│       ├── cliente_detail.html        # Detalle de cliente
│       ├── cliente_confirm_delete.html # Confirmar eliminación
│       └── pagination.html            # Componente de paginación compartido
│
├── tienda/                            # App: Tienda Online
│   ├── __init__.py
│   ├── admin.py                       # Configuración del admin para productos y categorías
│   ├── apps.py
│   ├── forms.py                       # Formularios para carrito, favoritos y filtros
│   ├── models.py                      # Categoria, Producto, Carrito, CarritoItem, Favorito
│   ├── urls.py                        # / (tienda) + /api/
│   ├── views.py                       # Productos, Carrito, Favoritos, API JSON
│   ├── tests.py                       # Tests de la app tienda
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── crear_productos.py     # Comando custom: crea productos de muestra
│   └── templates/tienda/
│       ├── lista_productos.html       # Catálogo con filtros de categoría, buscador y grid responsive
│       ├── detalle_producto.html      # Detalle con galería de imágenes, tallas, stock y acciones
│       ├── carrito.html               # Carrito de compras
│       └── favoritos.html             # Lista de favoritos (server-side)
│
├── manage.py                          # Script de gestión de Django
├── requirements.txt                   # Dependencias del proyecto
├── test_mysql.py                      # Test de conexión MySQL
├── .env                               # Variables de entorno (opcional)
├── diagramas.puml                     # Diagramas UML (PlantUML)
│
├── static/                            # Archivos estáticos globales
│   ├── css/
│   │   ├── style.css                  # Estilos personalizados (footer, auth pages)
│   │   ├── tienda.css                 # Estilos específicos de la tienda
│   │   ├── bootstrap.min.css          # Bootstrap 5.3 (local)
│   │   └── fontawesome.min.css        # Font Awesome (local)
│   ├── js/
│   │   ├── main.js                    # Scripts principales (SPA, funcionalidades generales)
│   │   ├── home.js                    # Página principal: carousel, filtros, buscador, favoritos, carrito, toast
│   │   ├── lista_productos.js         # Catálogo: filtros por categoría, favoritos, carrito, toast
│   │   ├── detalle_producto.js        # Detalle: cambio de imagen, favoritos, carrito, buy-now, toast
│   │   ├── favoritos.js               # Página favoritos: renderizado, eliminar, toast, badges
│   │   ├── bootstrap.bundle.min.js   # Bootstrap JS (local)
│   │   └── fontawesome.min.js         # Font Awesome JS (local)
│   └── img/
│       ├── logo.png                   # Logo de ANGELOW
│       ├── favico.ico                 # Favicon
│       ├── default-product.jpg        # Imagen placeholder
│       ├── general/                   # Iconos e imágenes para dashboard/admin
│       │   ├── logos.png              # Logos institucionales
│       │   ├── motico.png             # Icono/mascota
│       │   ├── panel.png              # Icono panel
│       │   ├── cliente.png            # Icono cliente
│       │   ├── categoria.png          # Icono categoría
│       │   ├── inventarios.png        # Icono inventarios
│       │   ├── carro.png              # Icono carrito
│       │   ├── favoritos.png          # Icono favoritos
│       │   ├── promedio.png           # Icono promedio
│       │   ├── ganancia.png           # Icono ganancia
│       │   ├── conversion.png         # Icono conversión
│       │   ├── analitica.png          # Icono analítica
│       │   ├── pedir.png              # Icono pedidos
│       │   ├── reparto.png            # Icono reparto
│       │   ├── logistica.png          # Icono logística
│       │   ├── reloj.png              # Icono tiempo
│       │   ├── visitante.png          # Icono visitante
│       │   ├── rebote.png             # Icono rebote
│       │   ├── volver.png             # Icono volver
│       │   └── contactenos.png        # Icono contáctenos
│       └── productos/                 # Imágenes de productos
│           ├── conjunto_size.png
│           ├── conjunto_jhogger.png
│           ├── conjunto_Deportive.png
│           └── vestido_verano.png
│
├── media/                             # Archivos subidos dinámicamente
│   └── productos/                     # Imágenes de productos cargadas por admin
│
├── logs/                              # Archivos de registro del sistema
│   ├── angelow.log                    # Log general de la aplicación
│   └── security.log                   # Log de eventos de seguridad
│
└── templates/                         # Templates globales del sistema
    └── admin/
        └── base_site.html             # Plantilla personalizada del admin
```

---

## 🗄️ Modelos de Base de Datos

### Tienda App

| Modelo | Campos principales |
|--------|-------------------|
| **Categoria** | nombre, slug, descripción, imagen |
| **Producto** | nombre, slug, categoría, subcategoría, precio, precio_oferta, descripción, tallas (JSON), stock, rating, activo, destacado, es_nuevo, imagenes (JSON) |
| **Carrito** | usuario (FK), fecha_creacion |
| **CarritoItem** | carrito (FK), producto (FK), talla, cantidad |
| **Favorito** | usuario (FK), producto (FK), fecha_agregado |

### Clientes App

| Modelo | Campos |
|--------|--------|
| **Cliente** | usuario (FK), nombre, email (único), teléfono, dirección, tipo_cliente (choices), notas, fecha_nacimiento, fecha_registro, fecha_actualizacion, actualizado_por (FK), is_active |

### Website App

| Modelo | Descripción |
|--------|-------------|
| **Usuario** | Extiende AbstractUser con email como username, rol (admin/vendedor/user), nombre, bloqueado_hasta, intentos_login |
| **Record** | Registro de recordatorios o notas del usuario |
| **ActividadUsuario** | Auditoría de actividades: tipo, descripción, IP, user_agent, fecha |

---

## 👥 Roles de Usuario y Permisos

| Rol | Permisos |
|-----|----------|
| **admin** | Acceso total: dashboard admin, CRM completo, importar/exportar clientes, auditoría |
| **vendedor** | Dashboard de usuario, CRM (crear/editar clientes propios), tienda |
| **user** | Dashboard de usuario, tienda, favoritos, perfil |

---

## 🔌 API Endpoints (JSON)

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/productos/` | GET | Lista de productos disponibles | ❌ |
| `/api/carrito/` | GET | Datos del carrito del usuario | ✅ |
| `/api/carrito/agregar/` | POST | Agregar producto al carrito | ✅ |
| `/api/favoritos/toggle/` | POST | Alternar favorito | ✅ |
| `/api/clientes/` | GET | Buscar clientes (JSON) | ✅ (admin/vendedor) |
| `/api/session/status/` | GET | Verificar estado de sesión | ✅ |

---

## 🛣️ Rutas Principales

### Tienda (Público)
| Ruta | Vista | Descripción |
|------|-------|-------------|
| `/` | `tienda:lista_productos` | Catálogo de productos con carousel, categorías y buscador |
| `/producto/<slug>/` | `tienda:detalle_producto` | Detalle de producto con galería y acciones |
| `/carrito/` | `tienda:ver_carrito` | Ver carrito de compras |
| `/carrito/agregar/<id>/` | `tienda:agregar_al_carrito` | Agregar al carrito |
| `/carrito/actualizar/<id>/` | `tienda:actualizar_carrito` | Actualizar cantidad |
| `/carrito/eliminar/<id>/` | `tienda:eliminar_del_carrito` | Eliminar item |
| `/favoritos/` | `tienda:favoritos` | Mis favoritos (tienda) |
| `/accounts/favorites/` | `website:favorites_view` | Mis favoritos (website) |
| `/api/productos/` | `tienda:api_productos` | JSON productos |
| `/api/clientes/` | `clientes:cliente_api` | JSON clientes |

### Autenticación y Usuarios
| Ruta | Vista | Descripción |
|------|-------|-------------|
| `/accounts/` | `website:home` | Redirección a dashboard |
| `/accounts/login/` | `website:login_view` | Iniciar sesión |
| `/accounts/register/` | `website:register_view` | Registrarse |
| `/accounts/logout/` | `website:logout_view` | Cerrar sesión |
| `/accounts/dashboard/admin/` | `website:dashboard_admin` | Dashboard de administrador |
| `/accounts/dashboard/user/` | `website:dashboard_user` | Dashboard de usuario regular |
| `/api/session/status/` | `website:session_status` | Estado de sesión (JSON) |

### CRM Clientes (Requiere Login)
| Ruta | Vista | Descripción |
|------|-------|-------------|
| `/clientes/` | `clientes:cliente_list` | Lista de clientes con filtros |
| `/clientes/nuevo/` | `clientes:cliente_create` | Crear cliente |
| `/clientes/editar/<id>/` | `clientes:cliente_update` | Editar cliente |
| `/clientes/eliminar/<id>/` | `clientes:cliente_delete` | Eliminar cliente (soft delete) |
| `/clientes/exportar/` | `clientes:cliente_export` | Exportar a CSV (solo admin) |
| `/clientes/importar/` | `clientes:cliente_import` | Importar desde CSV (solo admin) |

---

## 🛠️ Tecnologías y Dependencias

- **Backend:** Django 4.2.11, Python 3.10+
- **Frontend:** Bootstrap 5.3, Font Awesome 6.5, JavaScript Vanilla (ES6)
- **Base de Datos:** SQLite3 (desarrollo), MySQL (producción)
- **Seguridad:** django-csp, python-dotenv
- **CSS:** Estilos personalizados con CSS Grid, Flexbox y animaciones

---

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

# 5. Cargar productos de prueba (opcional)
python manage.py crear_productos

# 6. Crear superusuario para el panel admin
python manage.py createsuperuser

# 7. Ejecutar servidor de desarrollo
python manage.py runserver
```

### Acceder a la aplicación

- **Tienda (público):** http://localhost:8000/
- **Admin Django:** http://localhost:8000/admin/
- **Login:** http://localhost:8000/accounts/login/
- **Registro:** http://localhost:8000/accounts/register/
- **Favoritos:** http://localhost:8000/accounts/favorites/
- **CRM Clientes:** http://localhost:8000/clientes/ (requiere login)
- **Dashboard Admin:** http://localhost:8000/accounts/dashboard/admin/
- **Dashboard Usuario:** http://localhost:8000/accounts/dashboard/user/

---

## 📁 Funcionalidades del Frontend

### Página Principal (`home.html` + `home.js`)
- **Hero Carousel:** Carrusel animado con 5 diapositivas (tarjetas de regalo, promociones, envío gratis)
  - Navegación por botones anterior/siguiente y puntos indicadores
  - Progress bar animada que muestra el tiempo restante
  - Autoplay cada 6.5 segundos con pausa al hover
  - Soporte táctil para swipe en dispositivos móviles
- **Filtro de Categorías:** Pills interactivos (Todos, Niños, Niñas, Bebés, Edición especial, Oferta, Popular, Body's, Pijamas, Vestidos, Conjunto)
- **Buscador en Tiempo Real:** Filtrado instantáneo por nombre, subcategoría y categoría
- **Grid de Productos:** Tarjetas con hover effect (elevación + zoom en imagen)
- **Badges Dinámicos:** Oferta (rojo), Nuevo (verde), Destacado (azul)
- **Acciones por Producto:** Botón de comprar y botón de favorito (corazón rojo)

### Catálogo de Productos (`lista_productos.html` + `lista_productos.js`)
- **Filtros por Categoría:** Pills clickeables con estado activo
- **Badges de Producto:** Oferta, Nuevo, Destacado
- **Indicadores de Stock:** En stock (verde), Últimas unidades (amarillo), Sin stock (rojo)
- **Carrito y Favoritos:** Funcionalidad completa con localStorage
- **Toast Notifications:** Feedback visual al agregar/quitar productos

### Detalle de Producto (`detalle_producto.html` + `detalle_producto.js`)
- **Galería de Imágenes:** Cambio de imagen principal con thumbnails clickeables
- **Información Completa:** Nombre, categoría, precio, precio oferta, stock, descripción
- **Acciones:** Agregar al carrito, Compra rápida (buy now), Agregar a favoritos
- **Navegación SPA:** Click en cualquier parte de la tarjeta dirige al detalle

### Página de Favoritos (`favorites.html` + `favoritos.js`)
- **Header con Contador:** Muestra cantidad de favoritos con diseño moderno
- **Grid Responsive:** Tarjetas con animaciones fadeInUp
- **Eliminar con Animación:** Efecto slideOut al quitar producto
- **Estado Vacío:** Vista amigable cuando no hay favoritos
- **Sincronización:** Escucha cambios desde otras pestañas del navegador
- **Badges Actualizados:** Contadores en navbar y dropdown se actualizan automáticamente

### Funcionalidades JavaScript Compartidas

| Archivo | Funcionalidades |
|---------|----------------|
| `main.js` | Scripts generales, inicialización |
| `home.js` | Hero carousel, filtros categoría, buscador tiempo real, favoritos, carrito, toast |
| `lista_productos.js` | Filtros categoría, favoritos, carrito, toast |
| `detalle_producto.js` | Galería imágenes, favoritos, carrito, buy-now, toast |
| `favoritos.js` | Renderizado favoritos, eliminar, toast, badges |

**Características transversales:**
- 🛒 **Carrito Persistente:** Almacenado en `localStorage` con clave `angelow_cart`
- ❤️ **Favoritos Persistente:** Almacenado en `localStorage` con clave `angelow_favorites`
- 🔔 **Toast Notifications:** Sistema de notificaciones animadas con colores semánticos
- 🎨 **Diseño Responsive:** CSS Grid + media queries para móvil, tablet y desktop

---

## ⚙️ Configuración

### Variables de entorno (`.env`)

```env
# Django
SECRET_KEY=tu-clave-secreta-super-segura-aqui-generada-con-secrets-module
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (SQLite por defecto)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Para MySQL en producción:
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=nombre_base_datos
# DB_USER=usuario_mysql
# DB_PASSWORD=contraseña_mysql
# DB_HOST=localhost
# DB_PORT=3306

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Seguridad
LOGIN_ATTEMPTS_LIMIT=5
LOGIN_ATTEMPTS_TIMEOUT=900
SESSION_COOKIE_AGE=3600
SESSION_MAX_IDLE_TIME=1800
SESSION_MAX_TOTAL_TIME=28800
RATE_LIMIT_PER_MINUTE=60
```

### Middlewares de Seguridad

El proyecto implementa **5 middlewares personalizados** (`website/middleware.py`):

1. **SessionSecurityMiddleware** - Expiración de sesiones, verificación de IP/User-Agent, headers de seguridad
2. **LoginAttemptMiddleware** - Limitación de intentos de login, bloqueo por fuerza bruta
3. **ActivityLogMiddleware** - Registro de actividades de usuarios (auditoría automática)
4. **SecurityHeadersMiddleware** - Headers HTTP de seguridad (XSS, HSTS, etc.)
5. **RateLimitMiddleware** - Limitación de tasa de solicitudes por IP (anti-DoS)

---

## 🔒 Seguridad

Modelo de seguridad de **4 capas**:

### Capa 1: Autenticación
- 🛡️ Login con credenciales validadas
- 🚦 Registro con validaciones robustas
- 🔐 Bloqueo de cuentas por intentos fallidos
- ⏱️ Expiración de sesión (30 min inactividad, 8 horas máximo)

### Capa 2: Autorización
- 🎫 Sistema de roles (admin, vendedor, user)
- 🚦 Decoradores personalizados por vista
- 🚫 Acceso restringido por rol
- 🛡️ Rate limiting por IP (anti-DoS)

### Capa 3: Validación
- 🧹 Anti-SQLi, anti-XSS, anti-CRLF
- ✅ Validaciones regex en formularios y modelos
- 🛡️ Headers de seguridad HTTP

### Capa 4: Auditoría
- 📝 Registro completo de actividades
- 📊 Modelo `ActividadUsuario`
- 🕵️ Registro de IP y User-Agent
- 📁 Logs en `logs/` (angelow.log, security.log)

---

## 🧪 Testing

```bash
# Todos los tests
python manage.py test

# Por app
python manage.py test website
python manage.py test clientes
python manage.py test tienda

# Con verbosidad
python manage.py test -v 2
```

---

## 🎨 Frontend - Detalles Técnicos

### CSS Personalizado

| Archivo | Propósito |
|---------|-----------|
| `style.css` | Footer, estilos base para autenticación |
| `tienda.css` | Estilos específicos de la tienda |
| CSS inline en templates | Estilos específicos por página (home.html, favorites.html) |

### Componentes CSS Destacados

- **Hero Carousel:** Altura responsive (460px desktop, 390px tablet, 320px móvil)
- **Cards Grid:** `grid-template-columns: repeat(auto-fill, minmax(260px, 1fr))`
- **Toast Notifications:** Animación `slideIn` con transición de opacidad/translateX
- **Product Cards:** Hover con `translateY(-6px)` y `box-shadow`
- **Category Pills:** Estados activo/inactivo con transiciones suaves

### JavaScript - Características

| Archivo | Líneas | Funcionalidad |
|---------|--------|---------------|
| `home.js` | 480 | Carousel hero, filtros categoría, buscador tiempo real, favoritos, carrito, toast |
| `lista_productos.js` | 156 | Filtros categoría, favoritos, carrito, toast |
| `detalle_producto.js` | 158 | Galería imágenes, favoritos, carrito, buy-now, toast |
| `favoritos.js` | 132 | Renderizado grid, eliminar, toast, badges |

**Patrones JavaScript utilizados:**
- **LocalStorage:** Persistencia de carrito (`angelow_cart`) y favoritos (`angelow_favorites`)
- **Event Delegation:** Manejo de clicks en tarjetas de producto
- **IIFE:** Carousel como módulo autocontenido
- **DOMContentLoaded:** Inicialización de componentes
- **Storage Events:** Sincronización entre pestañas

---

## Dar de alta productos

1. Acceder a http://localhost:8000/admin/
2. Crear **Categorías** (Niño, Niña, Bebé, etc.)
3. Crear **Productos** con imágenes, precio, stock, tallas en JSON
4. O usar: `python manage.py crear_productos`

---

## 🚀 Despliegue

1. Configurar `DEBUG = False`
2. Configurar `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`
3. Migrar a MySQL: configurar `.env` y ejecutar `python manage.py migrate`
4. Configurar SSL: `SECURE_SSL_REDIRECT = True`
5. Recolectar estáticos: `python manage.py collectstatic`
6. Servidor WSGI (Gunicorn/uWSGI) + Nginx

---

## 🏗️ Arquitectura

- **Patrón MTV** de Django (Model-Template-View)
- **Organización por apps** con templates y staticfiles aislados
- **Principios SOLID y DRY** en modelos, vistas, formularios y middlewares
- **Validación server-side** estricta en forms, models y utils
- **API JSON** para desacoplamiento frontend/backend
- **SPA ligera** con JavaScript vanilla para experiencia interactiva
- **Localización** en español colombiano (`es-co`, `America/Bogota`)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'feat: agregar funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Pull Request

---

## 📄 Licencia

Proyecto privado - ANGELOW Colombia  
© 2026 ANGELOW. Todos los derechos reservados.

---

Desarrollado con ❤️ para ANGELOW - Ropa Infantil en Medellín, Colombia
