# website/views.py

"""
Vistas de la aplicación website para ANGELOW
Define vistas de autenticación, dashboard y gestión de usuarios
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
import logging
import re

# Importaciones del proyecto
from .forms import RegisterForm, LoginForm, RecordForm, PerfilUsuarioForm
from .models import Usuario, Record, ActividadUsuario
from clientes.models import Cliente
from tienda.models import Producto, Favorito

# Configurar logger para auditoría (Capa 4)
logger = logging.getLogger('website.security')

# ============================================================
# 1. DECORADORES PERSONALIZADOS (DRY)
# ============================================================

def role_required(allowed_roles=[]):
    """
    Decorador para verificar roles de usuario (Capa 2 - Autorización)
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                if request.user.rol in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'No tienes permisos para acceder a esta sección.')
                    return redirect('website:dashboard')
            else:
                return redirect('website:login')
        return wrapper_func
    return decorator

# ============================================================
# 2. VISTA DE INICIO (HOME)
# ============================================================

@never_cache
def home(request):
    """
    Vista principal del sitio
    Redirige al dashboard si el usuario está autenticado
    """
    if request.user.is_authenticated:
        return redirect('website:dashboard')
    
    # Productos destacados para la página de inicio
    productos_destacados = Producto.objects.filter(
        es_destacado=True,
        esta_activo=True,
        stock__gt=0
    ).order_by('-rating')[:6]
    
    context = {
        'productos_destacados': productos_destacados,
    }
    return render(request, 'website/home.html', context)

# ============================================================
# 3. VISTA DE LOGIN (Capa 1 - Autenticación)
# ============================================================

@never_cache
@csrf_protect
def login_view(request):
    """
    Vista de inicio de sesión con protección contra fuerza bruta
    
    Capas de seguridad:
    - Capa 1: Autenticación de usuario
    - Capa 2: Limitador de intentos (Capa 2)
    - Capa 3: Validación CSRF
    - Capa 4: Auditoría de intentos
    """
    # Redirigir si ya está autenticado
    if request.user.is_authenticated:
        return redirect('website:dashboard')
    
    # Obtener IP del cliente
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = f'login_attempts_{ip}'
    
    # Verificar intentos fallidos (Capa 2)
    attempts = cache.get(key, 0)
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        # Verificar límite de intentos
        if attempts >= settings.LOGIN_ATTEMPTS_LIMIT:
            logger.warning(f'Demasiados intentos de login desde IP: {ip}')
            messages.error(
                request,
                f'Demasiados intentos fallidos. Espera {settings.LOGIN_ATTEMPTS_TIMEOUT // 60} minutos.'
            )
            return render(request, 'website/login.html', {'form': form})
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Autenticar usuario
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Verificar si el usuario está activo
                if not user.is_active:
                    messages.error(request, 'Esta cuenta está deshabilitada.')
                    logger.warning(f'Intento de login a cuenta deshabilitada: {username} - IP: {ip}')
                    return render(request, 'website/login.html', {'form': form})
                
                # Verificar si el usuario está bloqueado
                if user.esta_bloqueado():
                    tiempo_restante = (user.bloqueado_hasta - timezone.now()).seconds // 60
                    messages.error(
                        request,
                        f'Cuenta bloqueada temporalmente. Espera {tiempo_restante} minutos.'
                    )
                    logger.warning(f'Intento de login a cuenta bloqueada: {username} - IP: {ip}')
                    return render(request, 'website/login.html', {'form': form})
                
                # Login exitoso
                login(request, user)
                
                # Resetear intentos fallidos (Capa 4)
                cache.delete(key)
                user.resetear_intentos()
                
                # Registrar sesión (Capa 4 - Auditoría)
                request.session['last_activity'] = timezone.now().isoformat()
                request.session['ip_address'] = ip
                request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
                
                # Registrar actividad (Capa 4)
                logger.info(f'Login exitoso: {user.username} desde IP: {ip}')
                
                # Crear registro de actividad
                ActividadUsuario.objects.create(
                    usuario=user,
                    tipo='login',
                    descripcion=f'Inicio de sesión desde IP: {ip}',
                    ip=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(
                    request,
                    f'¡Bienvenido de vuelta, {user.get_nombre_completo()}!'
                )
                
                # Redirigir según el rol
                if user.rol == 'admin':
                    return redirect('website:dashboard_admin')
                else:
                    return redirect('website:dashboard_user')
            
            # Login fallido - incrementar contador (Capa 2)
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, settings.LOGIN_ATTEMPTS_TIMEOUT)
            
            logger.warning(f'Intento de login fallido desde IP: {ip} - Intento #{attempts}')
            messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = LoginForm()
    
    return render(request, 'website/login.html', {'form': form})

# ============================================================
# 4. VISTA DE REGISTRO (Capa 1 - Autenticación)
# ============================================================

@never_cache
@csrf_protect
def register_view(request):
    """
    Vista de registro de nuevos usuarios
    
    Capas de seguridad:
    - Capa 1: Creación de usuario
    - Capa 3: Validaciones con expresiones regulares
    - Capa 4: Auditoría de registro
    """
    # Redirigir si ya está autenticado
    if request.user.is_authenticated:
        return redirect('website:dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                # Guardar usuario
                user = form.save()
                
                # Iniciar sesión automáticamente
                login(request, user)
                
                # Registrar actividad (Capa 4)
                ip = request.META.get('REMOTE_ADDR', 'unknown')
                logger.info(f'Nuevo usuario registrado: {user.email} desde IP: {ip}')
                
                ActividadUsuario.objects.create(
                    usuario=user,
                    tipo='creacion',
                    descripcion=f'Registro de nuevo usuario: {user.email}',
                    ip=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(
                    request,
                    f'¡Registro exitoso! Bienvenido a ANGELOW, {user.get_nombre_completo()}.'
                )
                
                # Redirigir según el rol
                if user.rol == 'admin':
                    return redirect('website:dashboard_admin')
                else:
                    return redirect('website:dashboard_user')
                
            except Exception as e:
                logger.error(f'Error en registro: {str(e)}')
                messages.error(request, 'Ocurrió un error durante el registro. Por favor, intenta nuevamente.')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = RegisterForm()
    
    return render(request, 'website/register.html', {'form': form})

# ============================================================
# 5. VISTA DE LOGOUT (Capa 4 - Auditoría)
# ============================================================

@login_required(login_url='website:login')
def logout_view(request):
    """
    Vista de cierre de sesión con auditoría
    """
    if request.user.is_authenticated:
        # Registrar actividad (Capa 4)
        logger.info(f'Logout: {request.user.username}')
        
        ActividadUsuario.objects.create(
            usuario=request.user,
            tipo='logout',
            descripcion='Cierre de sesión',
            ip=request.META.get('REMOTE_ADDR', 'unknown'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Cerrar sesión
        logout(request)
        messages.info(request, 'Has cerrado sesión exitosamente.')
    
    return redirect('website:login')

# ============================================================
# 6. DASHBOARD ADMIN (Capa 2 - Autorización)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def dashboard_admin(request):
    """
    Dashboard para administradores
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 2: Autorización (solo admin)
    - Capa 4: Auditoría de acceso
    """
    # Estadísticas para el dashboard
    total_usuarios = Usuario.objects.count()
    total_clientes = Cliente.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = 0  # Implementar con modelo de pedidos
    
    # Últimos registros
    ultimos_usuarios = Usuario.objects.order_by('-date_joined')[:5]
    ultimos_clientes = Cliente.objects.order_by('-fecha_registro')[:5]
    
    # Productos con bajo stock
    productos_bajo_stock = Producto.objects.filter(
        stock__lte=5,
        esta_activo=True
    ).order_by('stock')[:10]
    
    # Actividades recientes (Capa 4 - Auditoría)
    actividades_recientes = ActividadUsuario.objects.select_related('usuario').order_by('-fecha')[:10]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_clientes': total_clientes,
        'total_productos': total_productos,
        'total_pedidos': total_pedidos,
        'ultimos_usuarios': ultimos_usuarios,
        'ultimos_clientes': ultimos_clientes,
        'productos_bajo_stock': productos_bajo_stock,
        'actividades_recientes': actividades_recientes,
    }
    
    return render(request, 'website/dashboard_admin.html', context)

# ============================================================
# 7. DASHBOARD USUARIO (Capa 2 - Autorización)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['user', 'vendedor'])
def dashboard_user(request):
    """
    Dashboard para usuarios regulares
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 2: Autorización (user o vendedor)
    """
    user = request.user
    
    # Obtener favoritos del usuario
    favoritos = Favorito.objects.filter(
        usuario=user,
        producto__esta_activo=True
    ).select_related('producto')[:8]
    
    # Últimas actividades (Capa 4 - Auditoría)
    actividades = ActividadUsuario.objects.filter(
        usuario=user
    ).order_by('-fecha')[:5]
    
    context = {
        'usuario': user,
        'favoritos': favoritos,
        'actividades': actividades,
    }
    
    return render(request, 'website/dashboard_user.html', context)

# ============================================================
# 8. DASHBOARD GENERAL (Redirección)
# ============================================================

@login_required(login_url='website:login')
def dashboard_view(request):
    """
    Vista de dashboard que redirige según el rol del usuario
    """
    if request.user.rol == 'admin':
        return redirect('website:dashboard_admin')
    else:
        return redirect('website:dashboard_user')

# ============================================================
# 9. VISTA DE FAVORITOS (Para usuarios)
# ============================================================

@login_required(login_url='website:login')
def favorites_view(request):
    """
    Vista de productos favoritos del usuario
    """
    favoritos = Favorito.objects.filter(
        usuario=request.user,
        producto__esta_activo=True
    ).select_related('producto').order_by('-agregado')
    
    context = {
        'favoritos': favoritos,
        'total_favoritos': favoritos.count(),
    }
    
    return render(request, 'website/favorites.html', context)

# ============================================================
# 10. VISTA DE PERFIL DE USUARIO
# ============================================================

@login_required(login_url='website:login')
def perfil_view(request):
    """
    Vista para ver y editar el perfil del usuario
    """
    user = request.user
    
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado exitosamente!')
            return redirect('website:perfil')
    else:
        form = PerfilUsuarioForm(instance=user)
    
    context = {
        'form': form,
        'usuario': user,
    }
    
    return render(request, 'website/perfil.html', context)

# ============================================================
# 11. VISTA DE ACTIVIDADES (Solo admin)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def actividades_view(request):
    """
    Vista de auditoría de actividades (Capa 4)
    Solo accesible para administradores
    """
    actividades = ActividadUsuario.objects.select_related('usuario').order_by('-fecha')
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        actividades = actividades.filter(tipo=tipo)
    
    usuario_id = request.GET.get('usuario')
    if usuario_id:
        actividades = actividades.filter(usuario_id=usuario_id)
    
    context = {
        'actividades': actividades[:100],  # Últimas 100
        'tipos': ActividadUsuario.TIPOS_ACTIVIDAD,
        'usuarios': Usuario.objects.all(),
        'filtro_tipo': tipo,
        'filtro_usuario': usuario_id,
    }
    
    return render(request, 'website/actividades.html', context)

# ============================================================
# 12. API PARA VERIFICAR ESTADO DE SESIÓN
# ============================================================

@login_required(login_url='website:login')
def session_status(request):
    """
    API para verificar el estado de la sesión desde el frontend
    """
    return JsonResponse({
        'authenticated': True,
        'username': request.user.username,
        'nombre': request.user.get_nombre_completo(),
        'rol': request.user.rol,
        'session_time': request.session.get('last_activity'),
    })