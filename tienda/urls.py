from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('producto/<slug:slug>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('favoritos/', views.favoritos, name='favoritos'),
    path('favoritos/toggle/<int:producto_id>/', views.toggle_favorito, name='toggle_favorito'),
    
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/carrito/', views.get_cart, name='get_cart'),
    path('api/carrito/agregar/', views.add_to_cart_api, name='add_to_cart'),
    path('api/favoritos/toggle/', views.toggle_favorite_api, name='toggle_favorite'),
]