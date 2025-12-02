from django.urls import path
from . import views

urlpatterns = [
    # =======================================================
    # RUTAS DE LA TIENDA (FRONTEND)
    # =======================================================
    path('', views.tienda_index, name='tienda_index'),
    path('login/', views.tienda_login, name='tienda_login'),
    path('logout/', views.tienda_logout, name='tienda_logout'),
    path('registro/', views.tienda_registro, name='tienda_registro'),
    
    # Categorías de Productos
    path('productos/celulares/', views.tienda_celulares, name='tienda_celulares'),
    path('productos/laptops/', views.tienda_laptops, name='tienda_laptops'),
    path('productos/tablets/', views.tienda_tablets, name='tienda_tablets'),
    path('productos/airpods/', views.tienda_airpods, name='tienda_airpods'),
    path('productos/accesorios/', views.tienda_accesorios, name='tienda_accesorios'),  

    # =======================================================
    # RUTAS DEL CARRITO
    # =======================================================
    path('carrito/', views.tienda_ver_carrito, name='tienda_ver_carrito'),
    path('carrito/agregar/', views.tienda_agregar_al_carrito, name='tienda_agregar_al_carrito'),
    path('carrito/eliminar/<str:item_key>/', views.tienda_eliminar_del_carrito, name='tienda_eliminar_del_carrito'),
    path('carrito/actualizar/<str:item_key>/', views.tienda_actualizar_item_carrito, name='tienda_actualizar_item_carrito'),

    # =======================================================
    # RUTAS DE CHECKOUT (DIRECCIÓN -> PAGO -> RESUMEN -> FIN)
    # =======================================================
    path('checkout/direccion/', views.tienda_mostrar_direccion, name='tienda_mostrar_direccion'),
    path('checkout/guardar_direccion/', views.tienda_guardar_direccion, name='tienda_guardar_direccion'),
    
    # NUEVAS RUTAS DE PAGO Y FINALIZACIÓN
    path('checkout/pago/', views.tienda_pago, name='tienda_pago'),
    path('checkout/pago/guardar/', views.tienda_guardar_pago, name='tienda_guardar_pago'),
    path('checkout/resumen/', views.tienda_resumen_pedido, name='tienda_resumen_pedido'),
    path('checkout/finalizar/', views.tienda_finalizar_compra, name='tienda_finalizar_compra'),
    path('mis-pedidos/', views.tienda_mis_pedidos, name='tienda_mis_pedidos'),


    # =======================================================
    # RUTAS DEL SISTEMA DE ADMINISTRACIÓN (CRUD)
    # =======================================================
    path('admin/inicio/', views.inicio_crud, name='inicio_crud'),
    
    # --- CRUD USUARIO ---
    path('admin/usuario/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('admin/usuario/ver/', views.ver_usuario, name='ver_usuario'),
    path('admin/usuario/actualizar/<int:usuario_id>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('admin/usuario/realizar_actualizacion/<int:usuario_id>/', views.realizar_actualizacion_usuario, name='realizar_actualizacion_usuario'),
    path('admin/usuario/borrar/<int:usuario_id>/', views.borrar_usuario, name='borrar_usuario'),

    # --- CRUD PEDIDOS (Necesario para los botones dentro de Usuario) ---
    path('admin/pedido/actualizar/<int:pedido_id>/', views.actualizar_pedido, name='actualizar_pedido'),
    # Nota: Aunque borres desde el usuario, esta ruta sirve para borrar pedidos individuales si fuera necesario
    # O si decides usar la vista independiente de pedidos más adelante.
    
    # --- CRUD CELULAR ---
    path('admin/celular/agregar/', views.agregar_celular, name='agregar_celular'),
    path('admin/celular/ver/', views.ver_celular, name='ver_celular'),
    path('admin/celular/actualizar/<int:celular_id>/', views.actualizar_celular, name='actualizar_celular'),
    path('admin/celular/realizar_actualizacion/<int:celular_id>/', views.realizar_actualizacion_celular, name='realizar_actualizacion_celular'),
    path('admin/celular/borrar/<int:celular_id>/', views.borrar_celular, name='borrar_celular'),

    # --- CRUD LAPTOP ---
    path('admin/laptop/agregar/', views.agregar_laptop, name='agregar_laptop'),
    path('admin/laptop/ver/', views.ver_laptop, name='ver_laptop'),
    path('admin/laptop/actualizar/<int:laptop_id>/', views.actualizar_laptop, name='actualizar_laptop'),
    path('admin/laptop/realizar_actualizacion/<int:laptop_id>/', views.realizar_actualizacion_laptop, name='realizar_actualizacion_laptop'),
    path('admin/laptop/borrar/<int:laptop_id>/', views.borrar_laptop, name='borrar_laptop'),

    # --- CRUD AIRPOD ---
    path('admin/airpod/agregar/', views.agregar_airpod, name='agregar_airpod'),
    path('admin/airpod/ver/', views.ver_airpod, name='ver_airpod'),
    path('admin/airpod/actualizar/<int:airpod_id>/', views.actualizar_airpod, name='actualizar_airpod'),
    path('admin/airpod/realizar_actualizacion/<int:airpod_id>/', views.realizar_actualizacion_airpod, name='realizar_actualizacion_airpod'),
    path('admin/airpod/borrar/<int:airpod_id>/', views.borrar_airpod, name='borrar_airpod'),

    # --- CRUD TABLET ---
    path('admin/tablet/agregar/', views.agregar_tablet, name='agregar_tablet'),
    path('admin/tablet/ver/', views.ver_tablet, name='ver_tablet'),
    path('admin/tablet/actualizar/<int:tablet_id>/', views.actualizar_tablet, name='actualizar_tablet'),
    path('admin/tablet/realizar_actualizacion/<int:tablet_id>/', views.realizar_actualizacion_tablet, name='realizar_actualizacion_tablet'),
    path('admin/tablet/borrar/<int:tablet_id>/', views.borrar_tablet, name='borrar_tablet'),

    # --- CRUD ACCESORIO ---
    path('admin/accesorio/agregar/', views.agregar_accesorio, name='agregar_accesorio'),
    path('admin/accesorio/ver/', views.ver_accesorio, name='ver_accesorio'),
    path('admin/accesorio/actualizar/<int:accesorio_id>/', views.actualizar_accesorio, name='actualizar_accesorio'),
    path('admin/accesorio/realizar_actualizacion/<int:accesorio_id>/', views.realizar_actualizacion_accesorio, name='realizar_actualizacion_accesorio'),
    path('admin/accesorio/borrar/<int:accesorio_id>/', views.borrar_accesorio, name='borrar_accesorio'),
]