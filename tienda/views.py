# tienda/views.py

"""
Vistas de la aplicación tienda para ANGELOW
Define vistas para productos, carrito, favoritos y API
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models import Q
from django.utils import timezone
import json
import logging

from .models import Producto, Categoria, Carrito, CarritoItem, Favorito
from .forms import AgregarAlCarritoForm, ActualizarCarritoForm, ProductoFilterForm
from website.models import ActividadUsuario
from website.views import role_required

# Configurar logger para auditoría (Capa 4)
logger = logging.getLogger('website.security')

# ============================================================
# 1. FUNCIONES DE UTILIDAD (DRY)
# ============================================================

def _get_alert_icon(tag):
    """
    Retorna el ícono correspondiente al tipo de mensaje (DRY)
    """
    icons = {
        'success': '<i class="fas fa-check-circle"></i>',
        'error': '<i class="fas fa-exclamation-triangle"></i>',
        'warning': '<i class="fas fa-exclamation-circle"></i>',
        'info': '<i class="fas fa-info-circle"></i>',
    }
    return icons.get(tag, icons['info'])

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
# 2. LISTA DE PRODUCTOS con Filtros y Paginación
# ============================================================

@never_cache
def lista_productos(request):
    """
    Vista para listar productos con filtros, búsqueda y paginación
    
    Capas de seguridad:
    - Capa 3: Validación de parámetros GET
    - Capa 4: Auditoría de búsquedas
    """
    
    # Obtener todos los productos activos con stock
    productos = Producto.objects.filter(
        esta_activo=True,
        stock__gt=0
    ).select_related('categoria')
    
    categorias = Categoria.objects.filter(es_activa=True)
    
    # ============================================================
    # FORMULARIO DE FILTRO (DRY)
    # ============================================================
    
    filter_form = ProductoFilterForm(request.GET, categorias=categorias)
    filtro_aplicado = False
    
    if filter_form.is_valid():
        # Búsqueda por texto
        q = filter_form.cleaned_data.get('q')
        if q:
            productos = productos.filter(
                Q(nombre__icontains=q) |
                Q(subcategoria__icontains=q) |
                Q(categoria__nombre__icontains=q) |
                Q(descripcion__icontains=q)
            )
            filtro_aplicado = True
            # Registrar búsqueda (Capa 4 - Auditoría)
            logger.info(f'Búsqueda de productos: "{q}" desde IP: {_get_client_ip(request)}')
        
        # Filtro por categoría
        categoria_slug = filter_form.cleaned_data.get('categoria')
        if categoria_slug:
            categoria = get_object_or_404(Categoria, slug=categoria_slug)
            productos = productos.filter(categoria=categoria)
            filtro_aplicado = True
        
        # Filtro por precio
        precio_min = filter_form.cleaned_data.get('precio_min')
        if precio_min is not None:
            productos = productos.filter(precio__gte=precio_min)
            filtro_aplicado = True
        
        precio_max = filter_form.cleaned_data.get('precio_max')
        if precio_max is not None:
            productos = productos.filter(precio__lte=precio_max)
            filtro_aplicado = True
        
        # Filtro por talla
        talla = filter_form.cleaned_data.get('talla')
        if talla:
            productos = productos.filter(tallas__contains=talla)
            filtro_aplicado = True
        
        # Filtro por oferta
        en_oferta = filter_form.cleaned_data.get('en_oferta')
        if en_oferta:
            productos = productos.filter(precio_oferta__isnull=False)
            filtro_aplicado = True
        
        # Ordenamiento
        ordenar = filter_form.cleaned_data.get('ordenar')
        if ordenar:
            orden_mapping = {
                'precio_asc': 'precio',
                'precio_desc': '-precio',
                'nombre_asc': 'nombre',
                'nombre_desc': '-nombre',
                'rating_desc': '-rating',
                'nuevos': '-fecha_creacion',
            }
            if ordenar in orden_mapping:
                productos = productos.order_by(orden_mapping[ordenar])
    
    # ============================================================
    # PRODUCTOS DESTACADOS (Siempre visibles)
    # ============================================================
    
    productos_destacados = productos.filter(es_destacado=True)[:4]
    
    # ============================================================
    # PAGINACIÓN
    # ============================================================
    
    paginator = Paginator(productos, 12)  # 12 productos por página
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # ============================================================
    # CONTEXTO
    # ============================================================
    
    context = {
        'productos': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'categorias': categorias,
        'categoria_activa': filter_form.cleaned_data.get('categoria', 'todos'),
        'busqueda': filter_form.cleaned_data.get('q', ''),
        'filter_form': filter_form,
        'filtro_aplicado': filtro_aplicado,
        'productos_destacados': productos_destacados,
        'paginator': paginator,
    }
    
    return render(request, 'tienda/lista_productos.html', context)


# ============================================================
# 3. DETALLE DE PRODUCTO
# ============================================================

@never_cache
def detalle_producto(request, slug):
    """
    Vista para ver el detalle de un producto específico
    
    Capas de seguridad:
    - Capa 4: Auditoría de visualización
    """
    
    producto = get_object_or_404(Producto, slug=slug, esta_activo=True)
    
    # Verificar si el producto está en favoritos
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(
            usuario=request.user,
            producto=producto
        ).exists()
    
    # Productos relacionados (misma categoría)
    relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        esta_activo=True,
        stock__gt=0
    ).exclude(id=producto.id)[:4]
    
    # Formulario para agregar al carrito
    form = AgregarAlCarritoForm(tallas_disponibles=producto.tallas)
    
    # Crear datos del producto para JSON
    producto_data = {
        'id': producto.id,
        'nombre': producto.nombre,
        'slug': producto.slug,
        'precio': float(producto.precio),
        'precio_oferta': float(producto.precio_oferta) if producto.precio_oferta else None,
        'imagen': producto.get_imagen_principal_url(),
        'categoria': producto.categoria.nombre if producto.categoria else '',
        'stock': producto.stock
    }
    
    # Registrar visualización (Capa 4 - Auditoría)
    if request.user.is_authenticated:
        logger.info(f'Producto visualizado: {producto.nombre} por {request.user.username}')
    else:
        logger.info(f'Producto visualizado: {producto.nombre} por visitante anónimo')
    
    context = {
        'producto': producto,
        'es_favorito': es_favorito,
        'relacionados': relacionados,
        'form': form,
        'producto_json': json.dumps(producto_data, ensure_ascii=False)
    }
    
    return render(request, 'tienda/detalle_producto.html', context)


# ============================================================
# 4. CARRITO DE COMPRAS
# ============================================================

@login_required(login_url='website:login')
@never_cache
def ver_carrito(request):
    """
    Vista para ver el carrito de compras
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 4: Auditoría de acceso
    """
    
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('producto').all()
    
    # Calcular totales
    subtotal = sum(item.subtotal() for item in items)
    iva = Decimal('0.19')
    total_iva = int(iva * subtotal)
    total_final = int(subtotal + total_iva)
    
    # Registrar acceso (Capa 4 - Auditoría)
    logger.info(f'Carrito visualizado por: {request.user.username}')
    
    context = {
        'items': items,
        'subtotal': subtotal,
        'total_iva': total_iva,
        'total_final': total_final,
        'total_items': carrito.get_total_items(),
        'carrito_vacio': carrito.esta_vacio(),
    }
    
    return render(request, 'tienda/carrito.html', context)


# ============================================================
# 5. AGREGAR AL CARRITO
# ============================================================

@login_required(login_url='website:login')
@require_POST
@csrf_protect
@never_cache
def agregar_al_carrito(request, producto_id):
    """
    Vista para agregar un producto al carrito
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 3: Validación de formulario
    - Capa 4: Auditoría de acción
    """
    
    producto = get_object_or_404(Producto, id=producto_id, esta_activo=True)
    
    # Verificar stock
    if producto.stock <= 0:
        messages.error(
            request,
            f'{_get_alert_icon("error")} El producto "{producto.nombre}" no tiene stock disponible.'
        )
        return redirect('tienda:detalle_producto', slug=producto.slug)
    
    # Procesar formulario
    form = AgregarAlCarritoForm(request.POST, tallas_disponibles=producto.tallas)
    
    if form.is_valid():
        talla = form.cleaned_data['talla']
        cantidad = form.cleaned_data['cantidad']
        
        # Obtener carrito
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        
        # Verificar stock disponible
        if cantidad > producto.stock:
            messages.error(
                request,
                f'{_get_alert_icon("error")} Stock insuficiente. Solo quedan {producto.stock} unidades.'
            )
            return redirect('tienda:detalle_producto', slug=producto.slug)
        
        # Agregar al carrito
        item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            talla=talla,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            nueva_cantidad = item.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                messages.error(
                    request,
                    f'{_get_alert_icon("error")} No puedes agregar más de {producto.stock} unidades.'
                )
                return redirect('tienda:detalle_producto', slug=producto.slug)
            item.cantidad = nueva_cantidad
            item.save()
        
        # Registrar actividad (Capa 4 - Auditoría)
        _registrar_actividad(
            request,
            'creacion',
            f'Producto agregado al carrito: {producto.nombre} - Talla: {talla} - Cantidad: {cantidad}',
            {'producto_id': producto.id, 'talla': talla, 'cantidad': cantidad}
        )
        
        messages.success(
            request,
            f'{_get_alert_icon("success")} "{producto.nombre}" agregado al carrito correctamente.'
        )
        
        # Redirigir según preferencia
        if request.POST.get('continuar_comprando'):
            return redirect('tienda:lista_productos')
        return redirect('tienda:ver_carrito')
    
    # Error en el formulario
    messages.error(
        request,
        f'{_get_alert_icon("error")} Por favor, selecciona una talla válida.'
    )
    return redirect('tienda:detalle_producto', slug=producto.slug)


# ============================================================
# 6. ACTUALIZAR CARRITO
# ============================================================

@login_required(login_url='website:login')
@require_POST
@csrf_protect
@never_cache
def actualizar_carrito(request, item_id):
    """
    Vista para actualizar la cantidad de un item en el carrito
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 2: Verificación de propiedad del item
    - Capa 3: Validación de cantidad
    - Capa 4: Auditoría de acción
    """
    
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad < 1:
        # Eliminar item
        nombre_producto = item.producto.nombre
        item.delete()
        _registrar_actividad(
            request,
            'eliminacion',
            f'Producto eliminado del carrito: {nombre_producto}',
            {'producto_id': item.producto.id}
        )
        messages.info(
            request,
            f'{_get_alert_icon("info")} "{nombre_producto}" eliminado del carrito.'
        )
    else:
        # Validar stock
        if cantidad > item.producto.stock:
            messages.error(
                request,
                f'{_get_alert_icon("error")} Stock insuficiente. Máximo: {item.producto.stock} unidades.'
            )
        else:
            item.cantidad = cantidad
            item.save()
            _registrar_actividad(
                request,
                'edicion',
                f'Carrito actualizado: {item.producto.nombre} - Cantidad: {cantidad}',
                {'producto_id': item.producto.id, 'cantidad': cantidad}
            )
            messages.success(
                request,
                f'{_get_alert_icon("success")} Carrito actualizado correctamente.'
            )
    
    return redirect('tienda:ver_carrito')


# ============================================================
# 7. ELIMINAR DEL CARRITO
# ============================================================

@login_required(login_url='website:login')
@require_POST
@csrf_protect
@never_cache
def eliminar_del_carrito(request, item_id):
    """
    Vista para eliminar un item del carrito
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 2: Verificación de propiedad
    - Capa 4: Auditoría de acción
    """
    
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    nombre_producto = item.producto.nombre
    
    item.delete()
    
    _registrar_actividad(
        request,
        'eliminacion',
        f'Producto eliminado del carrito: {nombre_producto}',
        {'producto_id': item.producto.id}
    )
    
    messages.info(
        request,
        f'{_get_alert_icon("info")} "{nombre_producto}" eliminado del carrito.'
    )
    
    return redirect('tienda:ver_carrito')


# ============================================================
# 8. FAVORITOS
# ============================================================

@login_required(login_url='website:login')
@never_cache
def favoritos(request):
    """
    Vista para ver la lista de productos favoritos
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 4: Auditoría de acceso
    """
    
    favoritos_list = Favorito.objects.filter(
        usuario=request.user,
        producto__esta_activo=True
    ).select_related('producto').order_by('-agregado')
    
    logger.info(f'Favoritos visualizados por: {request.user.username}')
    
    context = {
        'favoritos': favoritos_list,
        'total_favoritos': favoritos_list.count(),
    }
    
    return render(request, 'tienda/favoritos.html', context)


# ============================================================
# 9. TOGGLE FAVORITO (Web)
# ============================================================

@login_required(login_url='website:login')
@require_POST
@csrf_protect
@never_cache
def toggle_favorito(request, producto_id):
    """
    Vista para agregar o quitar un producto de favoritos
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 4: Auditoría de acción
    """
    
    producto = get_object_or_404(Producto, id=producto_id, esta_activo=True)
    
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        producto=producto
    )
    
    if not created:
        favorito.delete()
        mensaje = f'"{producto.nombre}" eliminado de favoritos'
        tipo = 'info'
        _registrar_actividad(
            request,
            'eliminacion',
            f'Producto eliminado de favoritos: {producto.nombre}',
            {'producto_id': producto.id}
        )
    else:
        mensaje = f'"{producto.nombre}" agregado a favoritos'
        tipo = 'success'
        _registrar_actividad(
            request,
            'creacion',
            f'Producto agregado a favoritos: {producto.nombre}',
            {'producto_id': producto.id}
        )
    
    # Determinar redirección
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'tienda:lista_productos'))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'es_favorito': created,
            'mensaje': mensaje,
            'total_favoritos': Favorito.objects.filter(usuario=request.user).count()
        })
    
    messages.success(request, f'{_get_alert_icon(tipo)} {mensaje}')
    return redirect(next_url)


# ============================================================
# 10. API - PRODUCTOS (JSON)
# ============================================================

@require_GET
def api_productos(request):
    """
    API para obtener productos en formato JSON
    
    Capas de seguridad:
    - Capa 3: Validación de parámetros
    """
    
    productos = Producto.objects.filter(esta_activo=True, stock__gt=0)
    
    # Filtros
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria__slug=categoria)
    
    limit = request.GET.get('limit')
    if limit:
        try:
            productos = productos[:int(limit)]
        except ValueError:
            pass
    
    data = {
        'products': [
            {
                'id': p.id,
                'name': p.nombre,
                'category': p.categoria.nombre if p.categoria else '',
                'subcategory': p.subcategoria or '',
                'price': float(p.precio),
                'offer_price': float(p.precio_oferta) if p.precio_oferta else None,
                'description': p.descripcion,
                'sizes': p.tallas,
                'imgs': [p.imagen_principal.url] if p.imagen_principal else [],
                'stock': p.stock,
                'rating': float(p.rating),
                'reviews': p.reseñas,
                'features': p.caracteristicas,
                'slug': p.slug,
                'es_destacado': p.es_destacado,
                'en_oferta': p.precio_oferta is not None,
            }
            for p in productos
        ],
        'total': productos.count(),
    }
    
    return JsonResponse(data, safe=False)


# ============================================================
# 11. API - CARRITO (JSON)
# ============================================================

@login_required(login_url='website:login')
@require_GET
def api_carrito(request):
    """
    API para obtener el carrito del usuario en formato JSON
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    """
    
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('producto').all()
    
    cart_items = []
    subtotal = 0
    
    for item in items:
        subtotal_item = item.subtotal()
        subtotal += subtotal_item
        cart_items.append({
            'id': item.id,
            'producto_id': item.producto.id,
            'name': item.producto.nombre,
            'talla': item.talla,
            'cantidad': item.cantidad,
            'precio': float(item.producto.get_precio_final()),
            'precio_original': float(item.producto.precio),
            'imagen': item.producto.imagen_principal.url if item.producto.imagen_principal else '',
            'subtotal': float(subtotal_item),
        })
    
    iva = Decimal('0.19')
    total_iva = float(iva * subtotal)
    
    return JsonResponse({
        'items': cart_items,
        'subtotal': float(subtotal),
        'iva': total_iva,
        'total': float(subtotal + total_iva),
        'total_items': carrito.get_total_items(),
        'vacio': carrito.esta_vacio(),
    })


# ============================================================
# 12. API - AGREGAR AL CARRITO (JSON)
# ============================================================

@login_required(login_url='website:login')
@csrf_exempt
@require_http_methods(['POST'])
def api_agregar_carrito(request):
    """
    API para agregar producto al carrito (AJAX)
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 3: Validación de datos
    - Capa 4: Auditoría de acción
    """
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    
    producto_id = data.get('producto_id')
    talla = data.get('talla')
    cantidad = data.get('cantidad', 1)
    
    if not producto_id or not talla:
        return JsonResponse({'error': 'Producto y talla son requeridos'}, status=400)
    
    producto = get_object_or_404(Producto, id=producto_id, esta_activo=True)
    
    if producto.stock < cantidad:
        return JsonResponse({'error': 'Stock insuficiente'}, status=400)
    
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    item, created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        talla=talla,
        defaults={'cantidad': cantidad}
    )
    
    if not created:
        if item.cantidad + cantidad > producto.stock:
            return JsonResponse({'error': 'Stock insuficiente'}, status=400)
        item.cantidad += cantidad
        item.save()
    
    _registrar_actividad(
        request,
        'creacion',
        f'Producto agregado al carrito (API): {producto.nombre} - Talla: {talla}',
        {'producto_id': producto.id, 'talla': talla, 'cantidad': cantidad}
    )
    
    return JsonResponse({
        'success': True,
        'message': f'{producto.nombre} agregado al carrito',
        'total_items': carrito.get_total_items(),
        'item_id': item.id,
    })


# ============================================================
# 13. API - TOGGLE FAVORITO (JSON) - Alternar favorito con toggle
# ============================================================

@login_required(login_url='website:login')
@csrf_exempt
@require_POST
def api_toggle_favorito(request):
    """
    API para alternar favoritos (AJAX)
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 3: Validación de datos
    - Capa 4: Auditoría de acción
    """
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Datos inválidos'}, status=400)
    
    producto_id = data.get('producto_id')
    
    if not producto_id:
        return JsonResponse({'success': False, 'message': 'Producto ID es requerido'}, status=400)
    
    producto = get_object_or_404(Producto, id=producto_id, esta_activo=True)
    
    # Toggle: si existe, eliminarlo; si no, crearlo
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        producto=producto
    )
    
    if created:
        # Se agregó el favorito
        es_favorito = True
        message = f'{producto.nombre} agregado a favoritos'
        _registrar_actividad(
            request,
            'creacion',
            f'Producto agregado a favoritos (API): {producto.nombre}',
            {'producto_id': producto.id}
        )
    else:
        # Se eliminó el favorito
        favorito.delete()
        es_favorito = False
        message = f'{producto.nombre} eliminado de favoritos'
        _registrar_actividad(
            request,
            'eliminacion',
            f'Producto eliminado de favoritos (API): {producto.nombre}',
            {'producto_id': producto.id}
        )
    
    return JsonResponse({
        'success': True,
        'es_favorito': es_favorito,
        'message': message,
        'total_favoritos': Favorito.objects.filter(usuario=request.user).count()
    })