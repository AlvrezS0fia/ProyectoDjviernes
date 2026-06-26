# website/middleware.py

"""
Middleware de seguridad para ANGELOW
Aplicando las 4 capas de seguridad y principios SOLID

Capas de Seguridad implementadas:
1. Capa 1 - Autenticación: Verificación de sesión activa
2. Capa 2 - Autorización: Control de acceso por roles
3. Capa 3 - Validación: Verificación de integridad de sesión (IP, User-Agent)
4. Capa 4 - Auditoría: Logging de eventos de seguridad
"""

import logging
import re
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse

# Configurar logger para auditoría (Capa 4)
logger = logging.getLogger('website.security')

# ============================================================
# 1. SESSION SECURITY MIDDLEWARE (Capa 1, 3 y 4)
# ============================================================

class SessionSecurityMiddleware:
    """
    Middleware para seguridad de sesiones
    
    Funcionalidades:
    - Expiración de sesiones inactivas (Capa 1)
    - Verificación de IP y User-Agent (Capa 3)
    - Headers de seguridad (Capa 3)
    - Logging de eventos (Capa 4)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Tiempo máximo de inactividad en segundos (30 minutos)
        self.max_idle_time = getattr(settings, 'SESSION_MAX_IDLE_TIME', 1800)
        # Tiempo máximo total de sesión (8 horas)
        self.max_session_time = getattr(settings, 'SESSION_MAX_TOTAL_TIME', 28800)
    
    def __call__(self, request):
        # ============================================================
        # PROCESAR REQUEST (Antes de la vista)
        # ============================================================
        
        if request.user.is_authenticated:
            # --- Verificar inactividad (Capa 1) ---
            last_activity = request.session.get('last_activity')
            session_start = request.session.get('session_start')
            
            if last_activity:
                try:
                    last_time = timezone.datetime.fromisoformat(last_activity)
                    idle_seconds = (timezone.now() - last_time).total_seconds()
                    
                    # Expirar sesión por inactividad
                    if idle_seconds > self.max_idle_time:
                        logger.warning(
                            f'Sesión expirada por inactividad: {request.user.username} '
                            f'(Inactivo por {int(idle_seconds)} segundos)'
                        )
                        logout(request)
                        return self._redirect_with_message(
                            request, 
                            'Tu sesión ha expirado por inactividad. Por favor, inicia sesión nuevamente.',
                            'warning'
                        )
                except (ValueError, TypeError):
                    pass
            
            # --- Verificar tiempo total de sesión (Capa 1) ---
            if session_start:
                try:
                    start_time = timezone.datetime.fromisoformat(session_start)
                    total_seconds = (timezone.now() - start_time).total_seconds()
                    
                    if total_seconds > self.max_session_time:
                        logger.info(
                            f'Sesión expirada por tiempo máximo: {request.user.username} '
                            f'(Duración: {int(total_seconds)} segundos)'
                        )
                        logout(request)
                        return self._redirect_with_message(
                            request,
                            'Tu sesión ha expirado por seguridad. Por favor, inicia sesión nuevamente.',
                            'warning'
                        )
                except (ValueError, TypeError):
                    pass
            
            # --- Verificar IP (Capa 3) ---
            current_ip = self._get_client_ip(request)
            session_ip = request.session.get('ip_address')
            
            if session_ip and session_ip != current_ip:
                logger.warning(
                    f'Posible secuestro de sesión: {request.user.username} - '
                    f'IP cambió de {session_ip} a {current_ip}'
                )
                logout(request)
                return self._redirect_with_message(
                    request,
                    'Tu sesión ha sido invalidada por razones de seguridad.',
                    'danger'
                )
            
            # --- Verificar User-Agent (Capa 3) ---
            current_ua = request.META.get('HTTP_USER_AGENT', '')
            session_ua = request.session.get('user_agent')
            
            if session_ua and session_ua != current_ua:
                logger.warning(
                    f'Posible secuestro de sesión: {request.user.username} - '
                    f'User-Agent cambiado'
                )
                logout(request)
                return self._redirect_with_message(
                    request,
                    'Tu sesión ha sido invalidada por razones de seguridad.',
                    'danger'
                )
            
            # --- Actualizar datos de sesión (DRY) ---
            request.session['last_activity'] = timezone.now().isoformat()
            
            if not session_ip:
                request.session['ip_address'] = current_ip
            if not session_ua:
                request.session['user_agent'] = current_ua
            if not session_start:
                request.session['session_start'] = timezone.now().isoformat()
        
        # ============================================================
        # PROCESAR RESPONSE (Después de la vista)
        # ============================================================
        
        response = self.get_response(request)
        
        # --- Agregar Headers de Seguridad (Capa 3) ---
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # --- Cache-Control para páginas sensibles ---
        if request.path.startswith('/accounts/') or request.path.startswith('/admin/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
    # ============================================================
    # MÉTODOS AUXILIARES (DRY)
    # ============================================================
    
    def _get_client_ip(self, request):
        """
        Obtiene la IP real del cliente considerando proxies
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _redirect_with_message(self, request, message, level='warning'):
        """
        Redirige con mensaje usando el sistema de mensajes de Django
        """
        from django.contrib import messages
        getattr(messages, level)(request, message)
        return redirect('website:login')


# ============================================================
# 2. LOGIN ATTEMPT MIDDLEWARE (Capa 2 y 4)
# ============================================================

class LoginAttemptMiddleware:
    """
    Middleware para limitar intentos de login y prevenir ataques de fuerza bruta
    
    Capas:
    - Capa 2: Autorización - Limita el acceso
    - Capa 4: Auditoría - Registra intentos fallidos
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_attempts = getattr(settings, 'LOGIN_ATTEMPTS_LIMIT', 5)
        self.block_time = getattr(settings, 'LOGIN_ATTEMPTS_TIMEOUT', 300)  # 5 minutos
    
    def __call__(self, request):
        # Verificar si es una solicitud de login
        if request.path == reverse('website:login') and request.method == 'POST':
            ip = self._get_client_ip(request)
            key = f'login_attempts_{ip}'
            
            attempts = cache.get(key, 0)
            
            # Si excede el límite, bloquear (Capa 2)
            if attempts >= self.max_attempts:
                logger.warning(f'Demasiados intentos de login desde IP: {ip}')
                from django.contrib import messages
                messages.error(
                    request,
                    f'Demasiados intentos de inicio de sesión. '
                    f'Espera {self.block_time // 60} minutos.'
                )
                return HttpResponseForbidden(
                    'Demasiados intentos de inicio de sesión. '
                    'Por favor, espera unos minutos.'
                )
        
        response = self.get_response(request)
        
        # Registrar intentos de login (Capa 4)
        if request.path == reverse('website:login') and request.method == 'POST':
            ip = self._get_client_ip(request)
            key = f'login_attempts_{ip}'
            
            if request.user.is_authenticated:
                # Login exitoso - resetear contador
                cache.delete(key)
                logger.info(f'Login exitoso: {request.user.username} desde IP: {ip}')
            else:
                # Login fallido - incrementar contador
                attempts = cache.get(key, 0) + 1
                cache.set(key, attempts, self.block_time)
                logger.warning(f'Intento de login fallido desde IP: {ip} (Intento #{attempts})')
        
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# ============================================================
# 3. ACTIVITY LOG MIDDLEWARE (Capa 4 - Auditoría)
# ============================================================

class ActivityLogMiddleware:
    """
    Middleware para registrar actividades de usuarios (Auditoría)
    
    Capa 4: Registra todas las acciones importantes del usuario
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Registrar solo si el usuario está autenticado y NO es una solicitud AJAX
        # evitando registrar la misma solicitud múltiples veces
        if request.user.is_authenticated and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self._log_activity(request)
        
        response = self.get_response(request)
        return response
    
    def _log_activity(self, request):
        """
        Registra la actividad del usuario en el log
        """
        # Obtener información de la solicitud
        user = request.user
        path = request.path
        method = request.method
        
        # Determinar tipo de actividad
        activity_type = 'general'
        if path.startswith('/admin/'):
            activity_type = 'admin'
        elif path.startswith('/clientes/'):
            if method == 'POST':
                if '/nuevo/' in path or 'create' in path:
                    activity_type = 'creacion'
                elif '/editar/' in path or 'update' in path:
                    activity_type = 'edicion'
                elif '/eliminar/' in path or 'delete' in path:
                    activity_type = 'eliminacion'
        elif path.startswith('/tienda/'):
            if '/carrito/' in path:
                activity_type = 'carrito'
            elif '/favoritos/' in path:
                activity_type = 'favoritos'
        
        # Registrar en el log
        logger.info(
            f'Actividad: {user.username} - {method} {path} - '
            f'Tipo: {activity_type} - IP: {self._get_client_ip(request)}'
        )
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# ============================================================
# 4. SECURITY HEADERS MIDDLEWARE (Capa 3)
# ============================================================

class SecurityHeadersMiddleware:
    """
    Middleware para agregar headers de seguridad adicionales
    
    Capa 3: Protección contra vulnerabilidades comunes
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )
        
        # HSTS (solo en producción)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
        
        return response


# ============================================================
# 5. RATE LIMIT MIDDLEWARE (Capa 2)
# ============================================================

class RateLimitMiddleware:
    """
    Middleware para limitar la tasa de solicitudes por IP
    
    Capa 2: Protección contra ataques de denegación de servicio (DoS)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 60)  # 60 solicitudes por minuto
    
    def __call__(self, request):
        ip = self._get_client_ip(request)
        key = f'rate_limit_{ip}'
        
        # Obtener contador actual
        requests = cache.get(key, 0)
        
        if requests >= self.limit:
            logger.warning(f'Límite de tasa excedido desde IP: {ip}')
            return JsonResponse(
                {'error': 'Demasiadas solicitudes. Por favor, espera un momento.'},
                status=429  # Too Many Requests
            )
        
        # Incrementar contador
        cache.set(key, requests + 1, 60)  # Expira en 60 segundos
        
        response = self.get_response(request)
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip