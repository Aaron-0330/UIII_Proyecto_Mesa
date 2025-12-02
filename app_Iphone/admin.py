from django.contrib import admin
from .models import (
    Direccion, Usuario, Celular, Laptop, Tablet, Airpod, 
    Accesorio, Carrito, CarritoItem, Pedido, DetallePedido
)

# Registra todos los modelos
admin.site.register(Direccion)
admin.site.register(Usuario)
admin.site.register(Celular)
admin.site.register(Laptop)
admin.site.register(Tablet)
admin.site.register(Airpod)
admin.site.register(Accesorio)
admin.site.register(Carrito)
admin.site.register(CarritoItem)
admin.site.register(Pedido)
admin.site.register(DetallePedido)

# Volver a realizar las migraciones (Solo si Django lo requiere, si no, sólo 'migrate' es suficiente)
# python manage.py makemigrations 
# python manage.py migrate