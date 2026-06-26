# dcrm/settings.py

"""
Configuración del proyecto ANGELOW - CRM & Tienda Online
Desarrollado con Django 4.2.11
Aplicando principios SOLID, DRY y 4 capas de seguridad
"""

import os
import sys
from pathlib import Path

# ============================================================
# 1. CONFIGURACIÓN BASE DEL PROYECTO
# ============================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# 2. VARIABLES DE ENTORNO (DRY - Centralización)
# ============================================================

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

# Función para obtener variables de entorno con valores por defecto
def get_env_var(key, default=None, required=False):
    """Centraliza la obtención de variables de entorno (DRY)"""
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"La variable de entorno {key} es requerida")
    return value

# ============================================================
# 3. SEGURIDAD - CLAVES Y MODO DEBUG (Capa 1 de Seguridad)
# ============================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_var('SECRET_KEY', 'django-insecure-%d5%@ag*=+v0!%i58yzz#+q4_8voh*_g#tg0czp1qjtyx%o2q9')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Cambiar a False en producción

# Hosts permitidos (seguridad en producción)
ALLOWED_HOSTS = get_env_var('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,testserver').split(',')

# ============================================================
# 4. APLICACIONES INSTALADAS (Modularidad - SOLID)
# ============================================================

INSTALLED_APPS = [
    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps del Proyecto (SRP - Single Responsibility)
    'website',      # Autenticación y Dashboard
    'clientes',     # CRM - Customer Relationship Management
    'tienda',       # Tienda Online
    
    # Google OAuth
    'social_django',
]

# Configuración del Admin personalizado
ADMIN_SITE_HEADER = "ANGELOW - Administración"
ADMIN_SITE_TITLE = "Panel de Control ANGELOW"
ADMIN_INDEX_TITLE = "Bienvenido al Sistema de Gestión"

# ============================================================
# 5. MIDDLEWARE - Capas de Seguridad (Capa 2)
# ============================================================

MIDDLEWARE = [
    # Seguridad y rendimiento
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',  # Comentado para desarrollo
    
    # Sesiones y autenticación
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Middleware personalizado de seguridad (Capa 2, 3 y 4)
    'website.middleware.SessionSecurityMiddleware',   # Seguridad de sesión
    'website.middleware.LoginAttemptMiddleware',      # Limitador de intentos
    'website.middleware.ActivityLogMiddleware',       # Auditoría
    
    # Social Auth
    'social_django.middleware.SocialAuthExceptionMiddleware',
    
    # Mensajes y seguridad
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================
# 6. CONFIGURACIÓN DE URLs Y TEMPLATES
# ============================================================

ROOT_URLCONF = 'dcrm.urls'

# Evitar redirecciones de slash que pueden causar logs duplicados
APPEND_SLASH = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Templates globales
        ],
        'APP_DIRS': True,  # Busca templates en cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # Social Auth
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'dcrm.wsgi.application'

# ============================================================
# 7. BASE DE DATOS (Configuración flexible)
# ============================================================

# Configuración de base de datos con soporte para múltiples motores
DATABASE_ENGINE = get_env_var('DB_ENGINE', 'django.db.backends.sqlite3')
DATABASE_NAME = get_env_var('DB_NAME', 'db.sqlite3')

# Soporte para MySQL
if DATABASE_ENGINE == 'django.db.backends.mysql':
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================
# 8. AUTENTICACIÓN Y USUARIOS PERSONALIZADOS (Capa 1)
# ============================================================

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'website.Usuario'

# URLs de autenticación
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'  # <--- Redirige a la página principal (home)
LOGOUT_REDIRECT_URL = '/'

# ============================================================
# 9. BACKENDS DE AUTENTICACIÓN (Google OAuth)
# ============================================================

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',      # Google OAuth
    'django.contrib.auth.backends.ModelBackend',     # Autenticación por defecto
)

# ============================================================
# 10. GOOGLE OAUTH CONFIGURATION
# ============================================================

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = get_env_var('GOOGLE_OAUTH2_KEY', '360030211358-rk479b959ttderqgeei11b7m6cj7qe9n.apps.googleusercontent.com')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = get_env_var('GOOGLE_OAUTH2_SECRET', '')

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = [
    'first_name',
    'last_name',
    'email',
]

# Namespace para URLs sociales
SOCIAL_AUTH_URL_NAMESPACE = 'social'

# ============================================================
# 11. SOCIAL AUTH PIPELINE
# ============================================================

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',  # Asociar por email
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# ============================================================
# 12. SEGURIDAD AVANZADA - CAPAS 3 y 4
# ============================================================

# --- Configuración de Sesiones (Capa 3) ---
SESSION_COOKIE_SECURE = False  # True en producción (HTTPS)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Tiempo máximo de inactividad (30 minutos)
SESSION_MAX_IDLE_TIME = 1800

# Tiempo máximo total de sesión (8 horas)
SESSION_MAX_TOTAL_TIME = 28800

# --- Configuración CSRF (Capa 3) ---
CSRF_COOKIE_SECURE = False  # True en producción (HTTPS)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# CORREGIDO: Agregar esquema http://
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
]

# Si usas variables de entorno:
# CSRF_TRUSTED_ORIGINS = get_env_var('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

# --- Headers de Seguridad (Capa 4) ---
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 año en producción
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = False  # True en producción
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- X-Frame-Options ---
X_FRAME_OPTIONS = 'SAMEORIGIN'

# --- Silenciar advertencias de seguridad en desarrollo ---
SILENCED_SYSTEM_CHECKS = ['security.W019'] if DEBUG else []

# ============================================================
# 13. VALIDACIÓN DE CONTRASEÑAS (Capa 3 - Expresiones Regulares)
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Validador personalizado para caracteres especiales (expresiones regulares)
    {
        'NAME': 'website.utils.PasswordComplexityValidator',
    },
]

# ============================================================
# 14. ARCHIVOS ESTÁTICOS Y MEDIA
# ============================================================

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Para recolección en producción

# Media files (Archivos subidos por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# 15. INTERNACIONALIZACIÓN
# ============================================================

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ============================================================
# 16. MENSAJES Y NOTIFICACIONES (Alertas visuales)
# ============================================================

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ============================================================
# 17. CORREO ELECTRÓNICO (Para notificaciones)
# ============================================================

EMAIL_BACKEND = get_env_var(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = get_env_var('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(get_env_var('EMAIL_PORT', 587))
EMAIL_USE_TLS = get_env_var('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD', '')

# ============================================================
# 18. LOGGING - Auditoría y Seguridad (Capa 4)
# ============================================================

# Crear directorio de logs si no existe
LOGS_DIR = BASE_DIR / 'logs'
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'angelow.log'),
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'security.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Desactivar el logger 'django.server' para evitar logs duplicados de peticiones HTTP
        'django.server': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'website.security': {
            'handlers': ['console', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    }
}

# ============================================================
# 19. CONFIGURACIÓN ADICIONAL PARA PRODUCCIÓN
# ============================================================

# Solo en producción
if not DEBUG:
    # Forzar HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Headers de seguridad adicionales
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ============================================================
# 20. DEFAULT PRIMARY KEY FIELD
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# 21. VARIABLES GLOBALES PARA TEMPLATES
# ============================================================

SITE_NAME = "ANGELOW"
SITE_DESCRIPTION = "CRM & Tienda Online - Ropa Infantil"
SITE_YEAR = "2026"
CONTACT_EMAIL = "contacto@angelow.com"
CONTACT_PHONE = "+57 300 123 4567"

# ============================================================
# 22. RATELIMIT (Protección contra ataques de fuerza bruta)
# ============================================================

# Configuración para el limitador de intentos de login
LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_ATTEMPTS_TIMEOUT = 300  # 5 minutos en segundos
RATE_LIMIT_PER_MINUTE = 60