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
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import models
import logging
import json

# Importaciones del proyecto
from .forms import RegisterForm, LoginForm, RecordForm, PerfilUsuarioForm, ClienteForm
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
                    return redirect('website:home')
            else:
                return redirect('website:login')
        return wrapper_func
    return decorator


# ============================================================
# 2. VISTA DE INICIO (HOME) - CON TODOS LOS PRODUCTOS
# ============================================================

@never_cache
def home(request):
    """
    Vista principal del sitio - Página de inicio con todos los productos
    """
    # Obtener query de búsqueda
    query = request.GET.get('q', '').strip()
    
    # TODOS los productos activos
    productos = Producto.objects.filter(esta_activo=True)
    
    # Filtrar por búsqueda si existe
    if query:
        productos = productos.filter(
            models.Q(nombre__icontains=query) |
            models.Q(subcategoria__icontains=query) |
            models.Q(categoria__nombre__icontains=query) |
            models.Q(descripcion__icontains=query)
        )
    
    productos = productos.order_by('-fecha_creacion')
    
    # Productos destacados para sección especial
    productos_destacados = productos.filter(es_destacado=True)[:4]
    
    # IDs de productos favoritos para el usuario
    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(Favorito.objects.filter(
            usuario=request.user
        ).values_list('producto_id', flat=True))
    
    # Convertir productos a JSON para JavaScript
    productos_json = []
    for p in productos:
        productos_json.append({
            'id': p.id,
            'nombre': p.nombre,
            'slug': p.slug,
            'precio': float(p.precio),
            'stock': p.stock,
            'tallas': p.tallas,
            'categoria': {'nombre': p.categoria.nombre},
            'subcategoria': p.subcategoria,
            'imagen_principal': p.imagen_principal.url if p.imagen_principal else None,
            'es_destacado': p.es_destacado,
            'precio_oferta': float(p.precio_oferta) if p.precio_oferta else None,
        })
    
    context = {
        'productos': productos,
        'productos_destacados': productos_destacados,
        'productos_json': json.dumps(productos_json),
        'busqueda': query,
        'favoritos_ids': favoritos_ids,
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
    - Capa 2: Limitador de intentos
    - Capa 3: Validación CSRF
    - Capa 4: Auditoría de intentos
    """
    # Redirigir si ya está autenticado
    if request.user.is_authenticated:
        return redirect('website:home')
    
    # Obtener IP del cliente
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = 'login_attempts_' + ip
    
    # Verificar intentos fallidos (Capa 2)
    attempts = cache.get(key, 0)
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        # Verificar límite de intentos
        if attempts >= settings.LOGIN_ATTEMPTS_LIMIT:
            logger.warning('Demasiados intentos de login desde IP: ' + ip)
            messages.error(
                request,
                'Demasiados intentos fallidos. Espera ' + str(settings.LOGIN_ATTEMPTS_TIMEOUT // 60) + ' minutos.'
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
                    logger.warning('Intento de login a cuenta deshabilitada: ' + username + ' - IP: ' + ip)
                    return render(request, 'website/login.html', {'form': form})
                
                # Verificar si el usuario está bloqueado
                if user.esta_bloqueado():
                    tiempo_restante = (user.bloqueado_hasta - timezone.now()).seconds // 60
                    messages.error(
                        request,
                        'Cuenta bloqueada temporalmente. Espera ' + str(tiempo_restante) + ' minutos.'
                    )
                    logger.warning('Intento de login a cuenta bloqueada: ' + username + ' - IP: ' + ip)
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
                logger.info('Login exitoso: ' + user.username + ' desde IP: ' + ip)
                
                # Crear registro de actividad
                ActividadUsuario.objects.create(
                    usuario=user,
                    tipo='login',
                    descripcion='Inicio de sesión desde IP: ' + ip,
                    ip=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(
                    request,
                    '¡Bienvenido de vuelta, ' + user.get_nombre_completo() + '!'
                )
                
                # Redirigir a la página principal (HOME)
                return redirect('website:home')
            
            # Login fallido - incrementar contador (Capa 2)
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, settings.LOGIN_ATTEMPTS_TIMEOUT)
            
            logger.warning('Intento de login fallido desde IP: ' + ip + ' - Intento #' + str(attempts))
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
        return redirect('website:home')
    
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
                logger.info('Nuevo usuario registrado: ' + user.email + ' desde IP: ' + ip)
                
                ActividadUsuario.objects.create(
                    usuario=user,
                    tipo='creacion',
                    descripcion='Registro de nuevo usuario: ' + user.email,
                    ip=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(
                    request,
                    '¡Registro exitoso! Bienvenido a ANGELOW, ' + user.get_nombre_completo() + '.'
                )
                
                # Redirigir a la página principal (HOME)
                return redirect('website:home')
                
            except Exception as e:
                logger.error('Error en registro: ' + str(e))
                messages.error(request, 'Ocurrió un error durante el registro. Por favor, intenta nuevamente.')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, field.capitalize() + ': ' + error)
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
        logger.info('Logout: ' + request.user.username)
        
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
    
    return redirect('website:home')


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
# 9. VISTA DE FAVORITOS (Para usuarios) - CON FAVORITOS DEL USUARIO
# ============================================================

@login_required(login_url='website:login')
def favorites_view(request):
    """
    Vista de productos favoritos del usuario
    """
    # Obtener los favoritos del usuario autenticado
    favoritos_usuario = Favorito.objects.filter(
        usuario=request.user,
        producto__esta_activo=True
    ).select_related('producto')
    
    # Convertir favoritos a JSON para JavaScript
    productos_data = []
    for fav in favoritos_usuario:
        producto = fav.producto
        productos_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'slug': producto.slug,
            'precio': float(producto.precio),
            'precio_oferta': float(producto.precio_oferta) if producto.precio_oferta else None,
            'imagen': producto.get_imagen_principal_url(),
            'categoria': producto.categoria.nombre if producto.categoria else '',
            'stock': producto.stock
        })
    
    context = {
        'productos': favoritos_usuario,
        'productos_json': json.dumps(productos_data, ensure_ascii=False),
        'favoritos_ids': [p.id for p in favoritos_usuario]
    }
    
    return render(request, 'website/favorites.html', context)


# ============================================================
# 10. API: OBTENER FAVORITOS
# ============================================================

@login_required(login_url='website:login')
@require_GET
def api_favoritos(request):
    """
    API para obtener los productos favoritos del usuario
    """
    favoritos = Favorito.objects.filter(
        usuario=request.user,
        producto__esta_activo=True
    ).select_related('producto')
    
    data = {
        'success': True,
        'favoritos': [fav.producto.id for fav in favoritos],
        'total': favoritos.count()
    }
    return JsonResponse(data)


# ============================================================
# 11. API: TOGGLE FAVORITO
# ============================================================

@login_required(login_url='website:login')
@csrf_exempt
@require_POST
def api_toggle_favorito(request):
    """
    API para agregar o quitar un producto de favoritos
    """
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        
        if not producto_id:
            return JsonResponse({
                'success': False,
                'message': 'Producto ID es requerido'
            }, status=400)
        
        producto = Producto.objects.filter(id=producto_id, esta_activo=True).first()
        if not producto:
            return JsonResponse({
                'success': False,
                'message': 'Producto no encontrado'
            }, status=404)
        
        favorito, created = Favorito.objects.get_or_create(
            usuario=request.user,
            producto=producto
        )
        
        if not created:
            favorito.delete()
            es_favorito = False
            message = 'Producto eliminado de favoritos'
        else:
            es_favorito = True
            message = 'Producto agregado a favoritos'
        
        total = Favorito.objects.filter(usuario=request.user).count()
        
        return JsonResponse({
            'success': True,
            'es_favorito': es_favorito,
            'message': message,
            'total': total
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ============================================================
# 12. VISTA DE PERFIL DE USUARIO
# ============================================================

@login_required(login_url='website:login')
def perfil_view(request):
    """
    Vista para ver y editar el perfil del usuario.
    Si el usuario es admin, también gestiona clientes desde el perfil.
    """
    user = request.user

    if request.method == 'POST':
        if user.rol == 'admin':
            if 'crear_cliente' in request.POST:
                form_cliente = ClienteForm(request.POST)
                if form_cliente.is_valid():
                    cliente = form_cliente.save(commit=False)
                    cliente.usuario = user
                    cliente.actualizado_por = user
                    cliente.save()
                    messages.success(request, f'Cliente "{cliente.nombre}" creado exitosamente.')
                    return redirect('website:perfil')
            elif 'editar_cliente_id' in request.POST:
                cliente_id = request.POST.get('editar_cliente_id')
                cliente = get_object_or_404(Cliente, id=cliente_id)
                form_cliente = ClienteForm(request.POST, instance=cliente)
                if form_cliente.is_valid():
                    cliente = form_cliente.save(commit=False)
                    cliente.actualizado_por = user
                    cliente.save()
                    messages.success(request, f'Cliente "{cliente.nombre}" actualizado exitosamente.')
                    return redirect('website:perfil')
            elif 'activar_cliente_id' in request.POST:
                cliente_id = request.POST.get('activar_cliente_id')
                cliente = get_object_or_404(Cliente, id=cliente_id)
                cliente.activo = True
                cliente.actualizado_por = user
                cliente.save()
                messages.success(request, f'Cliente "{cliente.nombre}" reactivado exitosamente.')
                return redirect('website:perfil')
            elif 'desactivar_cliente_id' in request.POST:
                cliente_id = request.POST.get('desactivar_cliente_id')
                cliente = get_object_or_404(Cliente, id=cliente_id)
                cliente.activo = False
                cliente.actualizado_por = user
                cliente.save()
                messages.success(request, f'Cliente "{cliente.nombre}" desactivado exitosamente.')
                return redirect('website:perfil')

        form = PerfilUsuarioForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('website:perfil')
    else:
        form = PerfilUsuarioForm(instance=user)

    context = {
        'form': form,
        'usuario': user,
    }

    if user.rol == 'admin':
        clientes = Cliente.objects.all().order_by('-fecha_registro')
        form_cliente = ClienteForm()
        clientes_con_form = []
        for cliente in clientes:
            clientes_con_form.append((cliente, ClienteForm(instance=cliente)))

        context.update({
            'clientes': clientes,
            'clientes_con_form': clientes_con_form,
            'form_cliente': form_cliente,
        })

    return render(request, 'website/perfil.html', context)


# ============================================================
# 13. VISTA DE ACTIVIDADES (Solo admin)
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
# 14. API PARA VERIFICAR ESTADO DE SESIÓN
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


# ============================================================
# 15. GESTIÓN DE CLIENTES (CRUD - Solo admin)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def gestion_clientes(request):
    """
    Vista para que el administrador gestione todos los clientes
    Permite ver, buscar y filtrar clientes
    """
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    
    # Búsqueda
    q = request.GET.get('q', '')
    if q:
        clientes = clientes.filter(
            models.Q(nombre__icontains=q) |
            models.Q(apellido__icontains=q) |
            models.Q(email__icontains=q) |
            models.Q(telefono__icontains=q) |
            models.Q(identificacion__icontains=q)
        )
    
    # Filtro por estado
    estado = request.GET.get('estado')
    if estado and estado != 'todos':
        if estado == 'activo':
            clientes = clientes.filter(activo=True)
        elif estado == 'inactivo':
            clientes = clientes.filter(activo=False)
    
    context = {
        'clientes': clientes,
        'total_clientes': clientes.count(),
        'busqueda': q,
        'filtro_estado': estado or 'todos',
    }
    
    return render(request, 'website/gestion_clientes.html', context)


@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def cliente_crear(request):
    """
    Vista para crear un nuevo cliente
    """
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'<i class="fas fa-check-circle me-2"></i>Cliente "{cliente.nombre_completo}" creado exitosamente.')
            
            # Registrar actividad
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo='creacion',
                descripcion=f'Creó el cliente: {cliente.nombre_completo}',
                ip=request.META.get('REMOTE_ADDR', 'unknown'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return redirect('website:gestion_clientes')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Cliente',
        'accion': 'Crear Cliente'
    }
    
    return render(request, 'clientes/cliente_form.html', context)


@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def cliente_editar(request, cliente_id):
    """
    Vista para editar un cliente existente
    """
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente_actualizado = form.save()
            messages.success(request, f'<i class="fas fa-check-circle me-2"></i>Cliente "{cliente_actualizado.nombre_completo}" actualizado exitosamente.')
            
            # Registrar actividad
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo='edicion',
                descripcion=f'Editó el cliente: {cliente_actualizado.nombre_completo}',
                ip=request.META.get('REMOTE_ADDR', 'unknown'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return redirect('website:gestion_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
        'titulo': f'Editar Cliente: {cliente.nombre_completo}',
        'accion': 'Guardar Cambios'
    }
    
    return render(request, 'clientes/cliente_form.html', context)


@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def cliente_eliminar(request, cliente_id):
    """
    Vista para eliminar un cliente (soft delete)
    """
    cliente = get_object_or_404(Cliente, id=cliente_id)
    nombre_cliente = cliente.nombre_completo
    
    if request.method == 'POST':
        # Soft delete - desactivar en lugar de eliminar
        cliente.activo = False
        cliente.save()
        
        messages.success(request, f'<i class="fas fa-trash-alt me-2"></i>Cliente "{nombre_cliente}" desactivado exitosamente.')
        
        # Registrar actividad
        ActividadUsuario.objects.create(
            usuario=request.user,
            tipo='eliminacion',
            descripcion=f'Desactivó el cliente: {nombre_cliente}',
            ip=request.META.get('REMOTE_ADDR', 'unknown'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return redirect('website:gestion_clientes')
    
    context = {
        'cliente': cliente,
        'nombre_cliente': nombre_cliente,
    }
    
    return render(request, 'clientes/cliente_confirm_delete.html', context)


@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def cliente_activar(request, cliente_id):
    """
    Vista para reactivar un cliente desactivado
    """
    cliente = get_object_or_404(Cliente, id=cliente_id)
    nombre_cliente = cliente.nombre_completo
    
    if request.method == 'POST':
        cliente.activo = True
        cliente.save()
        
        messages.success(request, f'<i class="fas fa-check-circle me-2"></i>Cliente "{nombre_cliente}" reactivado exitosamente.')
        
        # Registrar actividad
        ActividadUsuario.objects.create(
            usuario=request.user,
            tipo='edicion',
            descripcion=f'Reactivó el cliente: {nombre_cliente}',
            ip=request.META.get('REMOTE_ADDR', 'unknown'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return redirect('website:gestion_clientes')
    
    return redirect('website:gestion_clientes')


@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def cliente_detalle(request, cliente_id):
    """
    Vista para ver el detalle de un cliente
    """
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    context = {
        'cliente': cliente,
    }
    
    return render(request, 'clientes/cliente_detail.html', context)