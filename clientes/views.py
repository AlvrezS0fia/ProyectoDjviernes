# clientes/views.py

"""
Vistas de la aplicación clientes para ANGELOW
Define el CRUD completo para la gestión de clientes (CRM)
Aplicando principios SOLID, DRY y seguridad (4 capas)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.utils import timezone
import logging

from .models import Cliente
from .forms import ClienteForm, ClienteFilterForm
from website.models import ActividadUsuario
from website.views import role_required

# Configurar logger para auditoría (Capa 4)
logger = logging.getLogger('website.security')

# ============================================================
# 1. LISTA DE CLIENTES (CRUD - Read) con Filtros y Paginación
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin', 'vendedor'])
@never_cache
def cliente_list(request):
    """
    Vista para listar todos los clientes con filtros y paginación
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 2: Autorización (admin o vendedor)
    - Capa 4: Auditoría de acceso
    """
    
    # Obtener todos los clientes
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    
    # ============================================================
    # FILTROS (DRY - Usando ClienteFilterForm)
    # ============================================================
    
    filter_form = ClienteFilterForm(request.GET)
    filtro_aplicado = False
    
    if filter_form.is_valid():
        # Filtro por nombre
        nombre = filter_form.cleaned_data.get('nombre')
        if nombre:
            clientes = clientes.filter(nombre__icontains=nombre)
            filtro_aplicado = True
        
        # Filtro por email
        email = filter_form.cleaned_data.get('email')
        if email:
            clientes = clientes.filter(email__icontains=email)
            filtro_aplicado = True
        
        # Filtro por tipo de cliente
        tipo_cliente = filter_form.cleaned_data.get('tipo_cliente')
        if tipo_cliente:
            clientes = clientes.filter(tipo_cliente=tipo_cliente)
            filtro_aplicado = True
        
        # Filtro por estado
        estado = filter_form.cleaned_data.get('estado')
        if estado == 'activo':
            clientes = clientes.filter(activo=True)
            filtro_aplicado = True
        elif estado == 'inactivo':
            clientes = clientes.filter(activo=False)
            filtro_aplicado = True
        
        # Filtro por fecha
        fecha_desde = filter_form.cleaned_data.get('fecha_desde')
        if fecha_desde:
            clientes = clientes.filter(fecha_registro__date__gte=fecha_desde)
            filtro_aplicado = True
        
        fecha_hasta = filter_form.cleaned_data.get('fecha_hasta')
        if fecha_hasta:
            clientes = clientes.filter(fecha_registro__date__lte=fecha_hasta)
            filtro_aplicado = True
    
    # ============================================================
    # PAGINACIÓN
    # ============================================================
    
    paginator = Paginator(clientes, 10)  # 10 clientes por página
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # ============================================================
    # ESTADÍSTICAS PARA EL DASHBOARD
    # ============================================================
    
    total_clientes = Cliente.objects.count()
    clientes_activos = Cliente.objects.filter(activo=True).count()
    clientes_vip = Cliente.objects.filter(tipo_cliente='vip').count()
    
    # Registrar acceso (Capa 4 - Auditoría)
    logger.info(f'Lista de clientes visualizada por: {request.user.username}')
    
    context = {
        'clientes': page_obj,
        'page_obj': page_obj,
        'is_paginated': True if paginator.num_pages > 1 else False,
        'filter_form': filter_form,
        'filtro_aplicado': filtro_aplicado,
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'clientes_vip': clientes_vip,
        'paginator': paginator,
    }
    
    return render(request, 'clientes/cliente_list.html', context)


# ============================================================
# 2. CREAR CLIENTE (CRUD - Create) con Validaciones y Auditoría
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin', 'vendedor'])
@never_cache
def cliente_create(request):
    """
    Vista para crear un nuevo cliente
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 2: Autorización (admin o vendedor)
    - Capa 3: Validaciones con expresiones regulares
    - Capa 4: Auditoría de creación
    """
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            try:
                cliente = form.save(commit=False)
                cliente.usuario = request.user
                cliente.actualizado_por = request.user
                cliente.save()
                
                # Registrar actividad (Capa 4 - Auditoría)
                logger.info(
                    f'Cliente creado: {cliente.nombre} - {cliente.email} '
                    f'por {request.user.username}'
                )
                
                ActividadUsuario.objects.create(
                    usuario=request.user,
                    tipo='creacion',
                    descripcion=f'Cliente creado: {cliente.nombre} - {cliente.email}',
                    ip=request.META.get('REMOTE_ADDR', 'unknown'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(
                    request,
                    f'¡Cliente "{cliente.nombre}" creado exitosamente!'
                )
                
                # Redirigir según la acción
                if '_add_another' in request.POST:
                    return redirect('clientes:cliente_create')
                else:
                    return redirect('clientes:cliente_list')
                
            except Exception as e:
                logger.error(f'Error al crear cliente: {str(e)}')
                messages.error(request, 'Ocurrió un error al crear el cliente.')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'object': None,
        'action': 'Crear',
        'accion': 'Crear',
        'titulo': 'Nuevo Cliente',
    }
    
    return render(request, 'clientes/cliente_form.html', context)


# ============================================================
# 3. ACTUALIZAR CLIENTE (CRUD - Update) con Auditoría
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin', 'vendedor'])
@never_cache
def cliente_update(request, pk):
    """
    Vista para actualizar un cliente existente
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 2: Autorización (admin o vendedor)
    - Capa 3: Validaciones con expresiones regulares
    - Capa 4: Auditoría de actualización
    """
    
    cliente = get_object_or_404(Cliente, pk=pk)
    
    # Verificar permisos adicionales (vendedor solo puede editar ciertos campos)
    if request.user.rol == 'vendedor' and cliente.usuario != request.user:
        messages.warning(request, 'Solo puedes editar clientes que hayas creado.')
        return redirect('clientes:cliente_list')
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        
        if form.is_valid():
            try:
                # Guardar cambios con auditoría
                cliente = form.save(commit=False)
                cliente.actualizado_por = request.user
                cliente.save()
                
                # Registrar actividad (Capa 4 - Auditoría)
                logger.info(
                    f'Cliente actualizado: {cliente.nombre} - {cliente.email} '
                    f'por {request.user.username}'
                )
                
                ActividadUsuario.objects.create(
                    usuario=request.user,
                    tipo='edicion',
                    descripcion=f'Cliente actualizado: {cliente.nombre} - {cliente.email}',
                    ip=request.META.get('REMOTE_ADDR', 'unknown'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(
                    request,
                    f'¡Cliente "{cliente.nombre}" actualizado exitosamente!'
                )
                
                return redirect('clientes:cliente_list')
                
            except Exception as e:
                logger.error(f'Error al actualizar cliente: {str(e)}')
                messages.error(request, 'Ocurrió un error al actualizar el cliente.')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'object': cliente,
        'action': 'Editar',
        'accion': 'Guardar Cambios',
        'titulo': f'Editar Cliente: {cliente.nombre}',
    }
    
    return render(request, 'clientes/cliente_form.html', context)


# ============================================================
# 4. ELIMINAR CLIENTE (CRUD - Delete) con Soft Delete
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
@never_cache
def cliente_delete(request, pk):
    """
    Vista para eliminar un cliente (Soft Delete)
    
    Capas de seguridad:
    - Capa 1: Autenticación requerida
    - Capa 2: Autorización (solo admin)
    - Capa 4: Auditoría de eliminación
    """
    
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        try:
            nombre_cliente = cliente.nombre
            email_cliente = cliente.email
            
            # Usar soft delete en lugar de eliminación física
            cliente.soft_delete(usuario=request.user)
            
            # Registrar actividad (Capa 4 - Auditoría)
            logger.info(
                f'Cliente eliminado (soft delete): {nombre_cliente} - {email_cliente} '
                f'por {request.user.username}'
            )
            
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo='eliminacion',
                descripcion=f'Cliente eliminado: {nombre_cliente} - {email_cliente}',
                ip=request.META.get('REMOTE_ADDR', 'unknown'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(
                request,
                f'¡Cliente "{nombre_cliente}" eliminado exitosamente!'
            )
            
            return redirect('clientes:cliente_list')
            
        except Exception as e:
            logger.error(f'Error al eliminar cliente: {str(e)}')
            messages.error(request, 'Ocurrió un error al eliminar el cliente.')
    
    context = {
        'object': cliente,
        'titulo': f'Eliminar Cliente: {cliente.nombre}',
    }
    
    return render(request, 'clientes/cliente_confirm_delete.html', context)


# ============================================================
# 5. VER DETALLE DE CLIENTE (Opcional)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin', 'vendedor'])
@never_cache
def cliente_detail(request, pk):
    """
    Vista para ver el detalle de un cliente específico
    """
    
    cliente = get_object_or_404(Cliente, pk=pk)
    
    # Verificar permisos
    if request.user.rol == 'vendedor' and cliente.usuario != request.user:
        messages.warning(request, 'No tienes permiso para ver este cliente.')
        return redirect('clientes:cliente_list')
    
    # Registrar acceso (Capa 4 - Auditoría)
    logger.info(
        f'Detalle de cliente visualizado: {cliente.nombre} '
        f'por {request.user.username}'
    )
    
    context = {
        'cliente': cliente,
        'titulo': f'Detalle de Cliente: {cliente.nombre}',
    }
    
    return render(request, 'clientes/cliente_detail.html', context)


# ============================================================
# 6. EXPORTAR CLIENTES (Opcional - Solo Admin)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def cliente_export(request):
    """
    Vista para exportar clientes a CSV
    """
    
    import csv
    from django.http import HttpResponse
    
    # Obtener clientes
    clientes = Cliente.objects.filter(activo=True)
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clientes_angelow.csv"'
    
    writer = csv.writer(response)
    
    # Escribir encabezados
    writer.writerow([
        'ID', 'Nombre', 'Email', 'Teléfono', 'Dirección', 
        'Tipo', 'Fecha Registro', 'Estado'
    ])
    
    # Escribir datos
    for cliente in clientes:
        writer.writerow([
            cliente.id,
            cliente.nombre,
            cliente.email,
            cliente.telefono or '',
            cliente.direccion or '',
            cliente.get_tipo_cliente_display(),
            cliente.fecha_registro.strftime('%Y-%m-%d %H:%M'),
            'Activo' if cliente.activo else 'Inactivo'
        ])
    
    # Registrar actividad (Capa 4 - Auditoría)
    logger.info(f'Clientes exportados por: {request.user.username}')
    
    return response


# ============================================================
# 7. API PARA CLIENTES (JSON)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin', 'vendedor'])
def cliente_api(request):
    """
    API para obtener clientes en formato JSON
    """
    
    clientes = Cliente.objects.filter(activo=True)
    
    # Filtro por búsqueda
    q = request.GET.get('q')
    if q:
        clientes = clientes.filter(
            Q(nombre__icontains=q) | Q(email__icontains=q)
        )
    
    # Limitar resultados
    clientes = clientes[:20]
    
    data = {
        'clientes': [
            {
                'id': c.id,
                'nombre': c.nombre,
                'email': c.email,
                'telefono': c.telefono or '',
                'direccion': c.direccion or '',
                'tipo': c.tipo_cliente,
                'tipo_display': c.get_tipo_cliente_display(),
                'fecha_registro': c.fecha_registro.strftime('%Y-%m-%d'),
            }
            for c in clientes
        ]
    }
    
    return JsonResponse(data)


# ============================================================
# 8. IMPORTAR CLIENTES (Opcional - Solo Admin)
# ============================================================

@login_required(login_url='website:login')
@role_required(allowed_roles=['admin'])
def cliente_import(request):
    """
    Vista para importar clientes desde un archivo CSV
    """
    
    from .forms import ClienteImportForm
    import csv
    import io
    
    if request.method == 'POST':
        form = ClienteImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            archivo = request.FILES['archivo']
            sobrescribir = form.cleaned_data.get('sobrescribir', False)
            
            # Leer archivo CSV
            decoded_file = archivo.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            clientes_creados = 0
            clientes_actualizados = 0
            errores = []
            
            for row in reader:
                try:
                    email = row.get('email', '').strip().lower()
                    nombre = row.get('nombre', '').strip()
                    
                    if not email or not nombre:
                        continue
                    
                    # Buscar cliente existente
                    cliente_existente = Cliente.objects.filter(email=email).first()
                    
                    if cliente_existente and sobrescribir:
                        # Actualizar cliente existente
                        cliente_existente.nombre = nombre
                        cliente_existente.telefono = row.get('telefono', '')
                        cliente_existente.direccion = row.get('direccion', '')
                        cliente_existente.tipo_cliente = row.get('tipo_cliente', 'regular')
                        cliente_existente.actualizado_por = request.user
                        cliente_existente.save()
                        clientes_actualizados += 1
                    elif not cliente_existente:
                        # Crear nuevo cliente
                        Cliente.objects.create(
                            nombre=nombre,
                            email=email,
                            telefono=row.get('telefono', ''),
                            direccion=row.get('direccion', ''),
                            tipo_cliente=row.get('tipo_cliente', 'regular'),
                            usuario=request.user,
                            actualizado_por=request.user
                        )
                        clientes_creados += 1
                except Exception as e:
                    errores.append(f'Error en fila: {row} - {str(e)}')
            
            # Mensaje de éxito
            if clientes_creados > 0 or clientes_actualizados > 0:
                messages.success(
                    request,
                    f'Importación completada: {clientes_creados} creados, {clientes_actualizados} actualizados.'
                )
            
            if errores:
                messages.warning(request, f'Se encontraron {len(errores)} errores en la importación.')
            
            # Registrar actividad (Capa 4 - Auditoría)
            logger.info(
                f'Clientes importados por: {request.user.username} - '
                f'{clientes_creados} creados, {clientes_actualizados} actualizados'
            )
            
            return redirect('clientes:cliente_list')
    else:
        form = ClienteImportForm()
    
    context = {
        'form': form,
        'titulo': 'Importar Clientes',
    }
    
    return render(request, 'clientes/cliente_import.html', context)