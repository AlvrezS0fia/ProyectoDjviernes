from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import json
from .models import Producto, Categoria, Carrito, CarritoItem, Favorito

def _get_alert_classes(tag):
    icons = {
        'success': '<i class="fas fa-check-circle"></i>',
        'error': '<i class="fas fa-exclamation-triangle"></i>',
        'warning': '<i class="fas fa-exclamation-circle"></i>',
        'info': '<i class="fas fa-info-circle"></i>',
    }
    return icons.get(tag, icons['info'])

def lista_productos(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(stock__gt=0)

    q = request.GET.get('q')
    if q:
        productos = productos.filter(
            models.Q(nombre__icontains=q) |
            models.Q(subcategoria__icontains=q) |
            models.Q(categoria__nombre__icontains=q)
        )

    cat_slug = request.GET.get('categoria')
    if cat_slug and cat_slug != 'todos':
        categoria = get_object_or_404(Categoria, slug=cat_slug)
        productos = productos.filter(categoria=categoria)

    context = {
        'categorias': categorias,
        'productos': productos,
        'categoria_activa': cat_slug or 'todos',
        'busqueda': q,
    }
    return render(request, 'tienda/lista_productos.html', context)

def detalle_producto(request, slug):
    producto = get_object_or_404(Producto, slug=slug)
    es_favorito = False
    if request.user.is_authenticated:
        es_favorito = Favorito.objects.filter(usuario=request.user, producto=producto).exists()
    return render(request, 'tienda/detalle_producto.html', {'producto': producto, 'es_favorito': es_favorito})

@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('producto').all()
    total = sum(item.subtotal() for item in items)
    iva = Decimal('0.19')
    total_iva = int(iva * total)
    total_final = int(total + total_iva)
    return render(request, 'tienda/carrito.html', {
        'items': items, 
        'total': total,
        'total_iva': total_iva,
        'total_final': total_final
    })

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    talla = request.POST.get('talla')
    if not talla:
        messages.warning(request, '<i class="fas fa-exclamation-circle me-2"></i>Selecciona una talla antes de continuar')
        return redirect('tienda:detalle_producto', slug=producto.slug)

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    item, created = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        talla=talla,
        defaults={'cantidad': 1}
    )
    if not created:
        if item.cantidad + 1 <= producto.stock:
            item.cantidad += 1
            item.save()
        else:
            messages.error(request, f'<i class="fas fa-times-circle me-2"></i>Stock insuficiente. Solo quedan {producto.stock} unidades')
            return redirect('tienda:detalle_producto', slug=producto.slug)

    messages.success(request, f'<i class="fas fa-shopping-cart me-2"></i>{producto.nombre} agregado al carrito correctamente')
    return redirect('tienda:ver_carrito')

@login_required
def actualizar_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    cantidad = int(request.POST.get('cantidad', 1))
    if cantidad < 1:
        item.delete()
        messages.info(request, '<i class="fas fa-trash me-2"></i>Producto eliminado del carrito')
    else:
        if cantidad <= item.producto.stock:
            item.cantidad = cantidad
            item.save()
            messages.success(request, '<i class="fas fa-check me-2"></i>Cantidad actualizada')
        else:
            messages.error(request, f'<i class="fas fa-exclamation-triangle me-2"></i>Stock insuficiente (máx. {item.producto.stock})')
    return redirect('tienda:ver_carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    nombre = item.producto.nombre
    item.delete()
    messages.info(request, f'<i class="fas fa-trash-alt me-2"></i>{nombre} eliminado del carrito')
    return redirect('tienda:ver_carrito')

@login_required
def favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('producto')
    return render(request, 'tienda/favoritos.html', {'favoritos': favoritos})

@login_required
def toggle_favorito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    favorito, created = Favorito.objects.get_or_create(usuario=request.user, producto=producto)
    if not created:
        favorito.delete()
        messages.info(request, f'{producto.nombre} eliminado de favoritos')
    else:
        messages.success(request, f'{producto.nombre} agregado a favoritos')
    return redirect(request.META.get('HTTP_REFERER', 'tienda:lista_productos'))

# ========== VISTAS API (para JavaScript) ==========
def api_productos(request):
    productos = Producto.objects.filter(stock__gt=0)
    data = []
    for p in productos:
        data.append({
            'id': p.id,
            'name': p.nombre,
            'category': p.categoria.nombre if p.categoria else '',
            'subcategory': p.subcategoria,
            'price': int(p.precio),
            'description': p.descripcion,
            'sizes': p.tallas,
            'imgs': [p.imagen_principal.url] if p.imagen_principal else [],
            'stock': p.stock,
            'rating': 4.5,
            'reviews': 0,
            'features': p.caracteristicas,
        })
    return JsonResponse({'products': data})

@login_required
def get_cart(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.select_related('producto')
    cart_items = []
    total = 0
    for item in items:
        subtotal = item.producto.precio * item.cantidad
        total += subtotal
        cart_items.append({
            'id': item.id,
            'producto_id': item.producto.id,
            'name': item.producto.nombre,
            'talla': item.talla,
            'cantidad': item.cantidad,
            'precio': int(item.producto.precio),
            'imagen': item.producto.imagen_principal.url if item.producto.imagen_principal else '',
            'subtotal': int(subtotal),
        })
    return JsonResponse({'items': cart_items, 'total': int(total)})

@csrf_exempt
@login_required
def add_to_cart_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        producto_id = data.get('producto_id')
        talla = data.get('talla')
        cantidad = data.get('cantidad', 1)
        producto = get_object_or_404(Producto, id=producto_id)
        if producto.stock < cantidad:
            return JsonResponse({'error': 'Stock insuficiente'}, status=400)
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        item, created = CarritoItem.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            talla=talla,
            defaults={'cantidad': cantidad}
        )
        if not created:
            item.cantidad += cantidad
            item.save()
        return JsonResponse({'status': 'ok', 'message': f'{producto.nombre} agregado'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@login_required
def toggle_favorite_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)
        producto_id = data.get('producto_id')
        producto = get_object_or_404(Producto, id=producto_id)
        fav, created = Favorito.objects.get_or_create(usuario=request.user, producto=producto)
        if not created:
            fav.delete()
            return JsonResponse({'status': 'removed', 'message': 'Eliminado de favoritos'})
        return JsonResponse({'status': 'added', 'message': 'Agregado a favoritos'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)