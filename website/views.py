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
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, csrf_exempt, ensure_csrf_cookie
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
# 2. VISTA DE INICIO (HOME)
# ============================================================

@never_cache
def home(request):
    """
    Vista principal del sitio - Página de inicio con todos los productos
    """
    query = request.GET.get('q', '').strip()
    
    productos = Producto.objects.filter(esta_activo=True)
    
    if query:
        productos = productos.filter(
            models.Q(nombre__icontains=query) |
            models.Q(subcategoria__icontains=query) |
            models.Q(categoria__nombre__icontains=query) |
            models.Q(descripcion__icontains=query)
        )
    
    productos = productos.order_by('-fecha_creacion')
    productos_destacados = productos.filter(es_destacado=True)[:4]
    
    favoritos_ids = []
    if request.user.is_authenticated:
        favoritos_ids = list(Favorito.objects.filter(
            usuario=request.user
        ).values_list('producto_id', flat=True))
    
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
    """
    if request.user.is_authenticated:
        return redirect('website:home')
    
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    key = 'login_attempts_' + ip
    attempts = cache.get(key, 0)
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if attempts >= settings.LOGIN_ATTEMPTS_LIMIT:
            logger.warning('Demasiados intentos de login desde IP: ' + ip)
            messages.error(request, 'Demasiados intentos fallidos. Espera ' + str(settings.LOGIN_ATTEMPTS_TIMEOUT // 60) + ' minutos.')
            return render(request, 'website/login.html', {'form': form})
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Esta cuenta está deshabilitada.')
                    logger.warning('Intento de login a cuenta deshabilitada: ' + username + ' - IP: ' + ip)
                    return render(request, 'website/login.html', {'form': form})
                
                if user.esta_bloqueado():
                    tiempo_restante = (user.bloqueado_hasta - timezone.now()).seconds // 60
                    messages.error(request, 'Cuenta bloqueada temporalmente. Espera ' + str(tiempo_restante) + ' minutos.')
                    logger.warning('Intento de login a cuenta bloqueada: ' + username + ' - IP: ' + ip)
                    return render(request, 'website/login.html', {'form': form})
                
                login(request, user)
                cache.delete(key)
                user.resetear_intentos()
                
                request.session['last_activity'] = timezone.now().isoformat()
                request.session['ip_address'] = ip
                request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
                
                logger.info('Login exitoso: ' + user.username + ' desde IP: ' + ip)
                
                ActividadUsuario.objects.create(
                    usuario=user,
                    tipo='login',
                    descripcion='Inicio de sesión desde IP: ' + ip,
                    ip=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, '¡Bienvenido de vuelta, ' + user.get_nombre_completo() + '!')
                return redirect('website:home')
            
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
    """
    if request.user.is_authenticated:
        return redirect('website:home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                
                ip = request.META.get('REMOTE_ADDR', 'unknown')
                logger.info('Nuevo usuario registrado: ' + user.email + ' desde IP: ' + ip)
                
                ActividadUsuario.objects.create(
                    usuario=user,
                    tipo='creacion',
                    descripcion='Registro de nuevo usuario: ' + user.email,
                    ip=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, '¡Registro exitoso! Bienvenido a ANGELOW, ' + user.get_nombre_completo() + '.')
                return redirect('website:home')
            except Exception as e:
                logger.error('Error en registro: ' + str(e))
                messages.error(request, 'Ocurrió un error durante el registro.')
        else:
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
        logger.info('Logout: ' + request.user.username)
        
        ActividadUsuario.objects.create(
            usuario=request.user,
            tipo='logout',
            descripcion='Cierre de sesión',
            ip=request.META.get('REMOTE_ADDR', 'unknown'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logout(request)
        messages.info(request, 'Has cerrado sesión exitosamente.')
    
    return redirect('website:home')


# ============================================================
# 6. DASHBOARD ADMIN (Capa 2 - Autorización) - CON CRUD COMPLETO
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def dashboard_admin(request):
    """
    Dashboard para administradores con gestión de clientes
    """
    # ============================================================
    # PROCESAR POST (Crear, Editar, Desactivar, Activar)
    # ============================================================
    
    if request.method == 'POST':
        # ---------- CREAR CLIENTE ----------
        if 'crear_cliente' in request.POST:
            identificacion = request.POST.get('identificacion')
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido', '')
            email = request.POST.get('email', '')
            telefono = request.POST.get('telefono', '')
            direccion = request.POST.get('direccion', '')
            ciudad = request.POST.get('ciudad', '')
            tipo_cliente = request.POST.get('tipo_cliente', 'regular')
            
            if identificacion and nombre:
                if Cliente.objects.filter(identificacion=identificacion).exists():
                    messages.error(request, 'Ya existe un cliente con esta identificación')
                else:
                    cliente = Cliente.objects.create(
                        identificacion=identificacion,
                        nombre=nombre,
                        apellido=apellido,
                        email=email,
                        telefono=telefono,
                        direccion=direccion,
                        ciudad=ciudad,
                        tipo_cliente=tipo_cliente,
                        activo=True
                    )
                    messages.success(request, f'Cliente "{cliente.nombre_completo}" creado')
            else:
                messages.error(request, 'Identificación y nombre son obligatorios')
            return redirect('website:dashboard_admin')
        
        # ---------- EDITAR CLIENTE ----------
        elif 'editar_cliente_id' in request.POST:
            cliente_id = request.POST.get('editar_cliente_id')
            cliente = get_object_or_404(Cliente, id=cliente_id)
            
            identificacion = request.POST.get('identificacion')
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido', '')
            email = request.POST.get('email', '')
            telefono = request.POST.get('telefono', '')
            direccion = request.POST.get('direccion', '')
            ciudad = request.POST.get('ciudad', '')
            tipo_cliente = request.POST.get('tipo_cliente', 'regular')
            
            if identificacion and nombre:
                if Cliente.objects.exclude(id=cliente_id).filter(identificacion=identificacion).exists():
                    messages.error(request, 'La identificación ya está en uso por otro cliente')
                else:
                    cliente.identificacion = identificacion
                    cliente.nombre = nombre
                    cliente.apellido = apellido
                    cliente.email = email
                    cliente.telefono = telefono
                    cliente.direccion = direccion
                    cliente.ciudad = ciudad
                    cliente.tipo_cliente = tipo_cliente
                    cliente.save()
                    messages.success(request, f'Cliente "{cliente.nombre_completo}" actualizado')
            else:
                messages.error(request, 'Identificación y nombre son obligatorios')
            return redirect('website:dashboard_admin')
        
        # ---------- DESACTIVAR CLIENTE ----------
        elif 'desactivar_cliente_id' in request.POST:
            cliente_id = request.POST.get('desactivar_cliente_id')
            cliente = get_object_or_404(Cliente, id=cliente_id)
            cliente.activo = False
            cliente.save()
            messages.success(request, f'Cliente desactivado')
            return redirect('website:dashboard_admin')
        
        # ---------- ACTIVAR CLIENTE ----------
        elif 'activar_cliente_id' in request.POST:
            cliente_id = request.POST.get('activar_cliente_id')
            cliente = get_object_or_404(Cliente, id=cliente_id)
            cliente.activo = True
            cliente.save()
            messages.success(request, f'Cliente reactivado')
            return redirect('website:dashboard_admin')
    
    # ============================================================
    # GET - Mostrar Dashboard
    # ============================================================
    
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    
    q = request.GET.get('q', '')
    if q:
        clientes = clientes.filter(
            models.Q(nombre__icontains=q) |
            models.Q(apellido__icontains=q) |
            models.Q(email__icontains=q) |
            models.Q(telefono__icontains=q) |
            models.Q(identificacion__icontains=q)
        )
    
    estado = request.GET.get('estado')
    if estado and estado != 'todos':
        if estado == 'activo':
            clientes = clientes.filter(activo=True)
        elif estado == 'inactivo':
            clientes = clientes.filter(activo=False)
    
    context = {
        'clientes': clientes,
        'total_clientes': Cliente.objects.count(),
        'clientes_activos': Cliente.objects.filter(activo=True).count(),
        'clientes_inactivos': Cliente.objects.filter(activo=False).count(),
        'clientes_nuevos': Cliente.objects.filter(fecha_registro__gte=timezone.now() - timezone.timedelta(days=30)).count(),
        'busqueda': q,
        'filtro_estado': estado or 'todos',
    }
    
    return render(request, 'website/dashboard_admin.html', context)


# ============================================================
# 7. DASHBOARD USUARIO
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['user', 'vendedor'])
def dashboard_user(request):
    """
    Dashboard para usuarios regulares
    """
    user = request.user
    
    favoritos = Favorito.objects.filter(
        usuario=user,
        producto__esta_activo=True
    ).select_related('producto')[:8]
    
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
# 9. VISTA DE FAVORITOS
# ============================================================

@login_required(login_url='website:login')
@ensure_csrf_cookie
def favorites_view(request):
    """
    Vista de productos favoritos del usuario
    """
    favoritos_usuario = Favorito.objects.filter(
        usuario=request.user,
        producto__esta_activo=True
    ).select_related('producto')
    
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
        'favoritos_ids': [p.id for p in favoritos_usuario],
        'csrf_token': get_token(request)
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
# 12. VISTA DE PERFIL DE USUARIO - CON CRUD DE CLIENTES
# ============================================================

@login_required(login_url='website:login')
def perfil_view(request):
    """
    Vista para ver y editar el perfil del usuario.
    Si el usuario es admin, redirige a la gestión de clientes.
    """
    user = request.user
    
    # ✅ Si es admin, redirigir directamente a gestión de clientes
    if user.rol == 'admin':
        return redirect('website:gestion_clientes')
    
    # Usuarios normales ven su perfil
    if request.method == 'POST':
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
    
    tipo = request.GET.get('tipo')
    if tipo:
        actividades = actividades.filter(tipo=tipo)
    
    usuario_id = request.GET.get('usuario')
    if usuario_id:
        actividades = actividades.filter(usuario_id=usuario_id)
    
    context = {
        'actividades': actividades[:100],
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
# 15. FUNCIONES DE UTILIDAD - AUDITORÍA (DRY)
# ============================================================

def _get_client_ip(request):
    """
    Obtiene la IP real del cliente (DRY)
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _registrar_actividad(request, tipo, descripcion, datos_adicionales=None):
    """
    Registra actividad en el sistema de auditoría (DRY - Capa 4)
    """
    if request.user.is_authenticated:
        ActividadUsuario.objects.create(
            usuario=request.user,
            tipo=tipo,
            descripcion=descripcion,
            ip=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            datos_adicionales=datos_adicionales or {}
        )


# ============================================================
# 16. GESTIÓN DE CLIENTES (CRUD - Solo admin)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def gestion_clientes(request):
    """
    Vista para que el administrador gestione todos los clientes
    """
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    
    q = request.GET.get('q', '')
    if q:
        clientes = clientes.filter(
            models.Q(nombre__icontains=q) |
            models.Q(apellido__icontains=q) |
            models.Q(email__icontains=q) |
            models.Q(telefono__icontains=q) |
            models.Q(identificacion__icontains=q)
        )
    
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
            messages.success(request, f'Cliente "{cliente.nombre_completo}" creado exitosamente.')
            _registrar_actividad(request, 'creacion', f'Creó el cliente: {cliente.nombre_completo}')
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
            messages.success(request, f'Cliente "{cliente_actualizado.nombre_completo}" actualizado exitosamente.')
            _registrar_actividad(request, 'edicion', f'Editó el cliente: {cliente_actualizado.nombre_completo}')
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
        cliente.activo = False
        cliente.save()
        messages.success(request, f'Cliente "{nombre_cliente}" desactivado exitosamente.')
        _registrar_actividad(request, 'eliminacion', f'Desactivó el cliente: {nombre_cliente}')
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
        messages.success(request, f'Cliente "{nombre_cliente}" reactivado exitosamente.')
        _registrar_actividad(request, 'edicion', f'Reactivó el cliente: {nombre_cliente}')
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