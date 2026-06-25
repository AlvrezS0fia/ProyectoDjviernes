# tienda/urls.py

from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    # ============================================================
    # PRODUCTOS
    # ============================================================
    path('', views.lista_productos, name='lista_productos'),
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle_producto'),
    
    # ============================================================
    # CARRITO (Web)
    # ============================================================
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    
    # ============================================================
    # FAVORITOS (Web)
    # ============================================================
    path('favoritos/', views.favoritos, name='favoritos'),
    path('favoritos/toggle/<int:producto_id>/', views.toggle_favorito, name='toggle_favorito'),
    
    # ============================================================
    # API (JSON) - PARA JAVASCRIPT
    # ============================================================
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/carrito/', views.api_carrito, name='api_carrito'),
    path('api/carrito/agregar/', views.api_agregar_carrito, name='api_agregar_carrito'),
    
    # ============================================================
    # API FAVORITOS - IMPORTANTE
    # ============================================================
    # GET: Obtener lista de favoritos
    path('api/favoritos/', views.api_favoritos, name='api_favoritos'),
    # POST: Agregar o quitar un favorito (toggle)
    path('api/favoritos/toggle/', views.api_toggle_favorito, name='api_toggle_favorito'),
]