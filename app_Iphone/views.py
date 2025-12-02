from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from decimal import Decimal
# IMPORTANTE: Se agregó MetodoPago a los imports
from .models import (
    Usuario, Direccion, MetodoPago, Celular, Laptop, Tablet, Airpod, Accesorio,
    Carrito, CarritoItem, Pedido, DetallePedido 
) 

# ==========================================================
# FUNCIONES AUXILIARES DEL CARRITO
# ==========================================================

def _get_product_model(product_type):
    """Retorna la clase del modelo de Django basada en el tipo de producto."""
    models_map = {
        'celular': Celular,
        'laptop': Laptop,
        'tablet': Tablet,
        'airpod': Airpod,
        'accesorio': Accesorio,
    }
    return models_map.get(product_type.lower())

def _get_cart_data(request):
    """
    Recupera los datos del carrito de la sesión, los enriquece con datos del modelo 
    y calcula el total. También actualiza el conteo de items en la sesión.
    """
    cart = request.session.get('cart', {})
    cart_items = []
    total_general = Decimal('0.00')
    item_count = 0
    items_to_delete = []

    for key, item in cart.items():
        product_type = item['type']
        product_id = item['id']
        cantidad = item['qty']
        
        Model = _get_product_model(product_type)
        if Model:
            try:
                product_obj = Model.objects.get(pk=product_id)
                precio = product_obj.precio
                subtotal = precio * cantidad
                nombre = getattr(product_obj, 'modelo', getattr(product_obj, 'tipo', 'Producto'))
                
                cart_items.append({
                    'key': key,
                    'type': product_type,
                    'id': product_id,
                    'nombre': nombre,
                    'generacion': getattr(product_obj, 'generacion', None),
                    'imagen_url': product_obj.imagen_url,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'subtotal': subtotal
                })
                
                total_general += subtotal
                item_count += cantidad
                
            except Model.DoesNotExist:
                items_to_delete.append(key)
        else:
            items_to_delete.append(key)

    if items_to_delete:
        for key in items_to_delete:
            if key in request.session['cart']:
                del request.session['cart'][key]
        request.session.modified = True
                
    request.session['cart_item_count'] = item_count

    return {'cart_items': cart_items, 'total_general': total_general, 'item_count': item_count}


# ==========================================================
# LÓGICA DEL CARRITO (NUEVAS VISTAS)
# ==========================================================

def tienda_ver_carrito(request):
    """Muestra la página con los contenidos del carrito."""
    cart_data = _get_cart_data(request)

    context = {
        'titulo': 'Mi Carrito de Compras',
        'cart_items': cart_data['cart_items'],
        'total_general': cart_data['total_general'],
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/carrito.html', context)

def tienda_agregar_al_carrito(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product_type = request.POST.get('product_type').lower()
        
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            cantidad = 1

        if cantidad < 1:
            cantidad = 1

        Model = _get_product_model(product_type)
        if not Model:
            return redirect(request.POST.get('next', 'tienda_index'))
            
        try:
            Model.objects.get(pk=product_id)
        except Model.DoesNotExist:
            return redirect(request.POST.get('next', 'tienda_index'))

        # Usar la sesión para almacenar el carrito
        cart = request.session.get('cart', {})
        item_key = f"{product_type}_{product_id}"

        if item_key in cart:
            cart[item_key]['qty'] += cantidad
        else:
            cart[item_key] = {
                'id': int(product_id), 
                'type': product_type,
                'qty': cantidad
            }

        request.session['cart'] = cart
        request.session.modified = True
        
        _get_cart_data(request) 

        return redirect(request.POST.get('next', 'tienda_ver_carrito'))

    return redirect('tienda_index')

def tienda_eliminar_del_carrito(request, item_key):
    """Elimina completamente un item del carrito."""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if item_key in cart:
            del cart[item_key]
            request.session['cart'] = cart
            request.session.modified = True
            _get_cart_data(request)
    return redirect('tienda_ver_carrito')

def tienda_actualizar_item_carrito(request, item_key):
    """Actualiza la cantidad de un item del carrito."""
    if request.method == 'POST':
        try:
            nueva_cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            return redirect('tienda_ver_carrito')
            
        if nueva_cantidad < 1:
            return tienda_eliminar_del_carrito(request, item_key)

        cart = request.session.get('cart', {})
        if item_key in cart:
            cart[item_key]['qty'] = nueva_cantidad
            request.session['cart'] = cart
            request.session.modified = True
            _get_cart_data(request)
            
    return redirect('tienda_ver_carrito')


# ==========================================================
# LÓGICA DE TIENDA (VISTAS PRINCIPALES)
# ==========================================================

def tienda_index(request):
    """Muestra la página principal de la tienda."""
    es_admin = request.session.get('es_admin', False)
    cart_data = _get_cart_data(request)
    
    context = {
        'titulo': 'Inicio - Tienda Apple',
        'es_admin': es_admin,
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/index.html', context)

def tienda_celulares(request):
    productos_celulares = Celular.objects.all()
    es_admin = request.session.get('es_admin', False)
    cart_data = _get_cart_data(request)
    
    context = {
        'titulo': 'Celulares - iPhone',
        'es_admin': es_admin,
        'productos_celulares': productos_celulares, 
        'hay_productos': productos_celulares.exists(), 
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/celulares.html', context)
    
def tienda_laptops(request):
    productos_laptops = Laptop.objects.all()
    es_admin = request.session.get('es_admin', False)
    cart_data = _get_cart_data(request)
    
    context = {
        'titulo': 'Laptops - MacBook',
        'es_admin': es_admin,
        'productos_laptops': productos_laptops,
        'hay_productos': productos_laptops.exists(),
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/laptops.html', context)

def tienda_tablets(request):
    productos_tablets = Tablet.objects.all()
    es_admin = request.session.get('es_admin', False)
    cart_data = _get_cart_data(request)
    
    context = {
        'titulo': 'Tablets - iPad',
        'es_admin': es_admin,
        'productos_tablets': productos_tablets,
        'hay_productos': productos_tablets.exists(),
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/tablets.html', context)

def tienda_airpods(request):
    productos_airpods = Airpod.objects.all()
    es_admin = request.session.get('es_admin', False)
    cart_data = _get_cart_data(request)
    
    context = {
        'titulo': 'Airpods - Apple',
        'es_admin': es_admin,
        'productos_airpods': productos_airpods,
        'hay_productos': productos_airpods.exists(),
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/airpods.html', context)

def tienda_accesorios(request):
    productos_accesorios = Accesorio.objects.all()
    es_admin = request.session.get('es_admin', False)
    cart_data = _get_cart_data(request)
    
    context = {
        'titulo': 'Accesorios - Apple',
        'es_admin': es_admin,
        'productos_accesorios': productos_accesorios,
        'hay_productos': productos_accesorios.exists(),
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/accesorios.html', context)

def tienda_login(request):
    """Maneja la lógica de inicio de sesión y redirección inteligente."""
    cart_data = _get_cart_data(request) 
    
    # Capturamos si hay una página siguiente pendiente (ej: ir al checkout)
    next_url = request.GET.get('next') or request.POST.get('next') or 'tienda_index'

    context = {
        'titulo': 'Iniciar Sesión',
        'cart_item_count': cart_data['item_count'],
        'next': next_url # Pasamos la url al template
    }

    if request.method == 'POST':
        email_ingresado = request.POST.get('email')
        pass_ingresada = request.POST.get('password')

        # Admin
        if email_ingresado == 'adminsoy@gmail.com' and pass_ingresada == 'eladmin':
            request.session['es_admin'] = True
            request.session['usuario_id'] = 0 
            return redirect('inicio_crud')
        
        # Usuario Normal
        try:
            usuario = Usuario.objects.get(email=email_ingresado)
            if usuario.contraseña == pass_ingresada:
                request.session['es_admin'] = False
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nombre'] = usuario.nombre
                
                # --- REDIRECCIÓN INTELIGENTE ---
                # Si venía del carrito, lo mandamos al checkout. Si no, al inicio.
                return redirect(next_url)
            else:
                return render(request, 'tienda/login.html', {'error': 'Contraseña incorrecta.', 'cart_item_count': cart_data['item_count'], 'next': next_url})
        except Usuario.DoesNotExist:
            return render(request, 'tienda/login.html', {'error': 'Usuario no encontrado.', 'cart_item_count': cart_data['item_count'], 'next': next_url})

    return render(request, 'tienda/login.html', context)

def tienda_logout(request):
    """Cierra la sesión del usuario."""
    request.session.clear()
    return redirect('tienda_index')

def tienda_registro(request):
    """Maneja el registro de usuarios desde la tienda."""
    cart_data = _get_cart_data(request) 
    context = {
        'titulo': 'Registro de Usuario',
        'cart_item_count': cart_data['item_count'],
        'datos': request.POST
    }

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        contraseña = request.POST.get('contraseña')
        
        if not all([nombre, email, telefono, contraseña]):
            context['error'] = 'Todos los campos son obligatorios.'
            return render(request, 'tienda/registro.html', context)
        
        try:
            nuevo_usuario = Usuario.objects.create(
                nombre=nombre,
                email=email,
                telefono=telefono,
                contraseña=contraseña,
                direccion=None,
                metodo_pago=None
            )

            request.session['es_admin'] = False
            request.session['usuario_id'] = nuevo_usuario.id
            request.session['usuario_nombre'] = nuevo_usuario.nombre
            return redirect('tienda_index') 
        
        except IntegrityError:
            context['error'] = 'El email ya está registrado.'
            return render(request, 'tienda/registro.html', context)
        except Exception as e:
            context['error'] = f'Ocurrió un error al registrar: {e}'
            return render(request, 'tienda/registro.html', context)

    return render(request, 'tienda/registro.html', context)


# ==========================================================
# VISTAS CRUD DE ADMINISTRACIÓN
# ==========================================================

def inicio_crud(request):
    """Página de inicio del sistema de administración."""
    if not request.session.get('es_admin'):
        return redirect('tienda_login')
    return render(request, 'crud/inicio.html', {'titulo': 'Inicio CRUD'})

# ----------------------------------------------------------
# AGREGAR USUARIO (MODIFICADO CON PAGOS)
# ----------------------------------------------------------
def agregar_usuario(request):
    """Crea Usuario, Dirección y Método de Pago."""
    if request.method == 'POST':
        # Datos del Usuario
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        contraseña = request.POST.get('contraseña')
        
        # Datos de la Dirección
        calle = request.POST.get('calle')
        codigo_postal = request.POST.get('codigo_postal')
        colonia = request.POST.get('colonia')
        ciudad = request.POST.get('ciudad')
        pais = request.POST.get('pais')

        # Datos del Método de Pago
        titular = request.POST.get('titular')
        numero_tarjeta = request.POST.get('numero_tarjeta')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        cvv = request.POST.get('cvv')
        
        try:
            # 1. Crear Dirección
            direccion_nueva = Direccion.objects.create(
                calle=calle, codigo_postal=codigo_postal,
                colonia=colonia, ciudad=ciudad, pais=pais
            )

            # 2. Crear Método de Pago
            pago_nuevo = MetodoPago.objects.create(
                titular=titular,
                numero_tarjeta=numero_tarjeta,
                fecha_vencimiento=fecha_vencimiento,
                cvv=cvv
            )
            
            # 3. Crear Usuario con ambas relaciones
            Usuario.objects.create(
                nombre=nombre,
                email=email,
                telefono=telefono,
                contraseña=contraseña, 
                direccion=direccion_nueva,
                metodo_pago=pago_nuevo
            )
            return redirect('ver_usuario') 

        except IntegrityError:
            # Limpieza si falla por email duplicado
            if 'direccion_nueva' in locals(): direccion_nueva.delete()
            if 'pago_nuevo' in locals(): pago_nuevo.delete()

            return render(request, 'crud/usuario/agregar_usuario.html', {
                'error': 'El email ya está registrado.', 
                'titulo': 'Agregar Usuario',
                'datos': request.POST 
            })
            
    return render(request, 'crud/usuario/agregar_usuario.html', {'titulo': 'Agregar Usuario'})

# ----------------------------------------------------------
# VER USUARIO
# ----------------------------------------------------------
def ver_usuario(request):
    """Muestra tabla de usuarios."""
    usuarios = Usuario.objects.all()
    context = {
        'usuarios': usuarios,
        'titulo': 'Ver Usuarios'
    }
    return render(request, 'crud/usuario/ver_usuario.html', context)

# ----------------------------------------------------------
# ACTUALIZAR USUARIO
# ----------------------------------------------------------
def actualizar_usuario(request, usuario_id):
    """Formulario para editar usuario, dirección y pago."""
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    # Obtenemos las relaciones para pasarlas al template
    direccion = usuario.direccion 
    metodo_pago = usuario.metodo_pago
    
    context = {
        'usuario': usuario,
        'direccion': direccion,
        'metodo_pago': metodo_pago,
        'titulo': 'Actualizar Usuario'
    }
    return render(request, 'crud/usuario/actualizar_usuario.html', context)

# ----------------------------------------------------------
# REALIZAR ACTUALIZACIÓN USUARIO (MODIFICADO)
# ----------------------------------------------------------
def realizar_actualizacion_usuario(request, usuario_id):
    """Procesa la actualización de todos los datos."""
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=usuario_id)
        
        # 1. Actualizar Usuario
        usuario.nombre = request.POST.get('nombre')
        usuario.email = request.POST.get('email')
        usuario.telefono = request.POST.get('telefono')
        nueva_contraseña = request.POST.get('contraseña')
        if nueva_contraseña:
            usuario.contraseña = nueva_contraseña
        
        # 2. Actualizar o Crear Dirección
        if usuario.direccion:
            dir_obj = usuario.direccion
        else:
            dir_obj = Direccion()
            
        dir_obj.calle = request.POST.get('calle')
        dir_obj.codigo_postal = request.POST.get('codigo_postal')
        dir_obj.colonia = request.POST.get('colonia')
        dir_obj.ciudad = request.POST.get('ciudad')
        dir_obj.pais = request.POST.get('pais')
        dir_obj.save()
        
        if not usuario.direccion:
            usuario.direccion = dir_obj

        # 3. Actualizar o Crear Método de Pago
        if usuario.metodo_pago:
            pago_obj = usuario.metodo_pago
        else:
            pago_obj = MetodoPago()

        pago_obj.titular = request.POST.get('titular')
        pago_obj.numero_tarjeta = request.POST.get('numero_tarjeta')
        pago_obj.fecha_vencimiento = request.POST.get('fecha_vencimiento')
        pago_obj.cvv = request.POST.get('cvv')
        pago_obj.save()

        if not usuario.metodo_pago:
            usuario.metodo_pago = pago_obj

        try:
            usuario.save()
            return redirect('ver_usuario')
        except IntegrityError:
            return render(request, 'crud/usuario/actualizar_usuario.html', {
                'usuario': usuario,
                'direccion': dir_obj,
                'metodo_pago': pago_obj,
                'error': 'El email ya está registrado.', 
                'titulo': 'Actualizar Usuario'
            })
            
    return redirect('ver_usuario')

# ----------------------------------------------------------
# BORRAR USUARIO
# ----------------------------------------------------------
def borrar_usuario(request, usuario_id):
    """Elimina usuario y opcionalmente sus datos asociados."""
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    
    if request.method == 'POST':
        # Borrar datos relacionados para evitar registros huérfanos
        if usuario.direccion:
            usuario.direccion.delete()
        if usuario.metodo_pago:
            usuario.metodo_pago.delete()
            
        usuario.delete()
        return redirect('ver_usuario')
        
    context = {
        'usuario': usuario,
        'titulo': 'Borrar Usuario'
    }
    return render(request, 'crud/usuario/borrar_usuario.html', context)


# ==========================================================
# VISTAS CRUD DE CELULAR
# ==========================================================

def agregar_celular(request):
    if request.method == 'POST':
        modelo = request.POST.get('modelo')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen_url = request.POST.get('imagen_url')
        try:
            Celular.objects.create(
                modelo=modelo, descripcion=descripcion,
                precio=precio, imagen_url=imagen_url
            )
            return redirect('ver_celular') 
        except Exception as e:
            return render(request, 'crud/celular/agregar_celular.html', {
                'error': f'{e}', 'titulo': 'Agregar Celular', 'datos': request.POST
            })
    return render(request, 'crud/celular/agregar_celular.html', {'titulo': 'Agregar Celular'})

def ver_celular(request):
    celulares = Celular.objects.all()
    return render(request, 'crud/celular/ver_celular.html', {'celulares': celulares, 'titulo': 'Ver Celulares'})

def actualizar_celular(request, celular_id):
    celular = get_object_or_404(Celular, pk=celular_id)
    return render(request, 'crud/celular/actualizar_celular.html', {'celular': celular, 'titulo': 'Actualizar Celular'})

def realizar_actualizacion_celular(request, celular_id):
    if request.method == 'POST':
        celular = get_object_or_404(Celular, pk=celular_id)
        celular.modelo = request.POST.get('modelo')
        celular.descripcion = request.POST.get('descripcion')
        celular.precio = request.POST.get('precio')
        celular.imagen_url = request.POST.get('imagen_url')
        try:
            celular.save()
            return redirect('ver_celular')
        except Exception as e:
            return render(request, 'crud/celular/actualizar_celular.html', {
                'celular': celular, 'error': f'{e}', 'titulo': 'Actualizar Celular'
            })
    return redirect('ver_celular')

def borrar_celular(request, celular_id):
    celular = get_object_or_404(Celular, pk=celular_id)
    if request.method == 'POST':
        celular.delete()
        return redirect('ver_celular')
    return render(request, 'crud/celular/borrar_celular.html', {'celular': celular, 'titulo': 'Borrar Celular'})


# ==========================================================
# VISTAS CRUD DE LAPTOP
# ==========================================================

def agregar_laptop(request):
    if request.method == 'POST':
        modelo = request.POST.get('modelo')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen_url = request.POST.get('imagen_url')
        try:
            Laptop.objects.create(
                modelo=modelo, descripcion=descripcion,
                precio=precio, imagen_url=imagen_url
            )
            return redirect('ver_laptop') 
        except Exception as e:
            return render(request, 'crud/laptop/agregar_laptop.html', {
                'error': f'{e}', 'titulo': 'Agregar Laptop', 'datos': request.POST
            })
    return render(request, 'crud/laptop/agregar_laptop.html', {'titulo': 'Agregar Laptop'})

def ver_laptop(request):
    laptops = Laptop.objects.all()
    return render(request, 'crud/laptop/ver_laptop.html', {'laptops': laptops, 'titulo': 'Ver Laptops'})

def actualizar_laptop(request, laptop_id):
    laptop = get_object_or_404(Laptop, pk=laptop_id)
    return render(request, 'crud/laptop/actualizar_laptop.html', {'laptop': laptop, 'titulo': 'Actualizar Laptop'})

def realizar_actualizacion_laptop(request, laptop_id):
    if request.method == 'POST':
        laptop = get_object_or_404(Laptop, pk=laptop_id)
        laptop.modelo = request.POST.get('modelo')
        laptop.descripcion = request.POST.get('descripcion')
        laptop.precio = request.POST.get('precio')
        laptop.imagen_url = request.POST.get('imagen_url')
        try:
            laptop.save()
            return redirect('ver_laptop')
        except Exception as e:
            return render(request, 'crud/laptop/actualizar_laptop.html', {
                'laptop': laptop, 'error': f'{e}', 'titulo': 'Actualizar Laptop'
            })
    return redirect('ver_laptop')

def borrar_laptop(request, laptop_id):
    laptop = get_object_or_404(Laptop, pk=laptop_id)
    if request.method == 'POST':
        laptop.delete()
        return redirect('ver_laptop')
    return render(request, 'crud/laptop/borrar_laptop.html', {'laptop': laptop, 'titulo': 'Borrar Laptop'})


# ==========================================================
# VISTAS CRUD DE AIRPOD
# ==========================================================

def agregar_airpod(request):
    if request.method == 'POST':
        generacion = request.POST.get('generacion')
        modelo = request.POST.get('modelo')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen_url = request.POST.get('imagen_url')
        try:
            Airpod.objects.create(
                generacion=generacion, modelo=modelo, descripcion=descripcion,
                precio=precio, imagen_url=imagen_url
            )
            return redirect('ver_airpod') 
        except Exception as e:
            return render(request, 'crud/airpod/agregar_airpod.html', {
                'error': f'{e}', 'titulo': 'Agregar Airpod', 'datos': request.POST
            })
    return render(request, 'crud/airpod/agregar_airpod.html', {'titulo': 'Agregar Airpod'})

def ver_airpod(request):
    airpods = Airpod.objects.all()
    return render(request, 'crud/airpod/ver_airpod.html', {'airpods': airpods, 'titulo': 'Ver Airpods'})

def actualizar_airpod(request, airpod_id):
    airpod = get_object_or_404(Airpod, pk=airpod_id)
    return render(request, 'crud/airpod/actualizar_airpod.html', {'airpod': airpod, 'titulo': 'Actualizar Airpod'})

def realizar_actualizacion_airpod(request, airpod_id):
    if request.method == 'POST':
        airpod = get_object_or_404(Airpod, pk=airpod_id)
        airpod.generacion = request.POST.get('generacion')
        airpod.modelo = request.POST.get('modelo')
        airpod.descripcion = request.POST.get('descripcion')
        airpod.precio = request.POST.get('precio')
        airpod.imagen_url = request.POST.get('imagen_url')
        try:
            airpod.save()
            return redirect('ver_airpod')
        except Exception as e:
            return render(request, 'crud/airpod/actualizar_airpod.html', {
                'airpod': airpod, 'error': f'{e}', 'titulo': 'Actualizar Airpod'
            })
    return redirect('ver_airpod')

def borrar_airpod(request, airpod_id):
    airpod = get_object_or_404(Airpod, pk=airpod_id)
    if request.method == 'POST':
        airpod.delete()
        return redirect('ver_airpod')
    return render(request, 'crud/airpod/borrar_airpod.html', {'airpod': airpod, 'titulo': 'Borrar Airpod'})


# ==========================================================
# VISTAS CRUD DE TABLET
# ==========================================================

def agregar_tablet(request):
    if request.method == 'POST':
        modelo = request.POST.get('modelo')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen_url = request.POST.get('imagen_url')
        try:
            Tablet.objects.create(
                modelo=modelo, descripcion=descripcion,
                precio=precio, imagen_url=imagen_url
            )
            return redirect('ver_tablet') 
        except Exception as e:
            return render(request, 'crud/tablet/agregar_tablet.html', {
                'error': f'{e}', 'titulo': 'Agregar Tablet', 'datos': request.POST
            })
    return render(request, 'crud/tablet/agregar_tablet.html', {'titulo': 'Agregar Tablet'})

def ver_tablet(request):
    tablets = Tablet.objects.all()
    return render(request, 'crud/tablet/ver_tablet.html', {'tablets': tablets, 'titulo': 'Ver Tablets'})

def actualizar_tablet(request, tablet_id):
    tablet = get_object_or_404(Tablet, pk=tablet_id)
    return render(request, 'crud/tablet/actualizar_tablet.html', {'tablet': tablet, 'titulo': 'Actualizar Tablet'})

def realizar_actualizacion_tablet(request, tablet_id):
    if request.method == 'POST':
        tablet = get_object_or_404(Tablet, pk=tablet_id)
        tablet.modelo = request.POST.get('modelo')
        tablet.descripcion = request.POST.get('descripcion')
        tablet.precio = request.POST.get('precio')
        tablet.imagen_url = request.POST.get('imagen_url')
        try:
            tablet.save()
            return redirect('ver_tablet')
        except Exception as e:
            return render(request, 'crud/tablet/actualizar_tablet.html', {
                'tablet': tablet, 'error': f'{e}', 'titulo': 'Actualizar Tablet'
            })
    return redirect('ver_tablet')

def borrar_tablet(request, tablet_id):
    tablet = get_object_or_404(Tablet, pk=tablet_id)
    if request.method == 'POST':
        tablet.delete()
        return redirect('ver_tablet')
    return render(request, 'crud/tablet/borrar_tablet.html', {'tablet': tablet, 'titulo': 'Borrar Tablet'})


# ==========================================================
# VISTAS CRUD DE ACCESORIO
# ==========================================================

def agregar_accesorio(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        modelo_compatible = request.POST.get('modelo_compatible')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen_url = request.POST.get('imagen_url')
        try:
            Accesorio.objects.create(
                tipo=tipo, modelo_compatible=modelo_compatible, descripcion=descripcion,
                precio=precio, imagen_url=imagen_url
            )
            return redirect('ver_accesorio') 
        except Exception as e:
            return render(request, 'crud/accesorio/agregar_accesorio.html', {
                'error': f'{e}', 'titulo': 'Agregar Accesorio', 'datos': request.POST
            })
    return render(request, 'crud/accesorio/agregar_accesorio.html', {'titulo': 'Agregar Accesorio'})

def ver_accesorio(request):
    accesorios = Accesorio.objects.all()
    return render(request, 'crud/accesorio/ver_accesorio.html', {'accesorios': accesorios, 'titulo': 'Ver Accesorios'})

def actualizar_accesorio(request, accesorio_id):
    accesorio = get_object_or_404(Accesorio, pk=accesorio_id)
    return render(request, 'crud/accesorio/actualizar_accesorio.html', {'accesorio': accesorio, 'titulo': 'Actualizar Accesorio'})

def realizar_actualizacion_accesorio(request, accesorio_id):
    if request.method == 'POST':
        accesorio = get_object_or_404(Accesorio, pk=accesorio_id)
        accesorio.tipo = request.POST.get('tipo')
        accesorio.modelo_compatible = request.POST.get('modelo_compatible')
        accesorio.descripcion = request.POST.get('descripcion')
        accesorio.precio = request.POST.get('precio')
        accesorio.imagen_url = request.POST.get('imagen_url')
        try:
            accesorio.save()
            return redirect('ver_accesorio')
        except Exception as e:
            return render(request, 'crud/accesorio/actualizar_accesorio.html', {
                'accesorio': accesorio, 'error': f'{e}', 'titulo': 'Actualizar Accesorio'
            })
    return redirect('ver_accesorio')

def borrar_accesorio(request, accesorio_id):
    accesorio = get_object_or_404(Accesorio, pk=accesorio_id)
    if request.method == 'POST':
        accesorio.delete()
        return redirect('ver_accesorio')
    return render(request, 'crud/accesorio/borrar_accesorio.html', {'accesorio': accesorio, 'titulo': 'Borrar Accesorio'})


# ==========================================================
# CHECKOUT TIENDA (DIRECCIÓN)
# ==========================================================

def tienda_mostrar_direccion(request):
    """Muestra el formulario de dirección para Checkout."""
    if not request.session.get('usuario_id'):
        return redirect('tienda_login')

    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    direccion_actual = usuario.direccion 
    cart_data = _get_cart_data(request)

    context = {
        'titulo': 'Dirección de Envío',
        'direccion': direccion_actual,
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/checkout_direccion.html', context)

def tienda_guardar_direccion(request):
    """Procesa el formulario y guarda/actualiza la Dirección del Usuario."""
    # 1. Verificar si es POST (si le dieron click al botón)
    if request.method == 'POST':
        if not request.session.get('usuario_id'):
            return redirect('tienda_login')

        usuario_id = request.session.get('usuario_id')
        usuario = get_object_or_404(Usuario, pk=usuario_id)

        # 2. Obtener la Dirección actual o crear una nueva
        if usuario.direccion:
            direccion_obj = usuario.direccion
        else:
            direccion_obj = Direccion()
            
        # 3. Guardar los datos del formulario en el objeto
        direccion_obj.calle = request.POST.get('calle')
        direccion_obj.codigo_postal = request.POST.get('codigo_postal')
        direccion_obj.colonia = request.POST.get('colonia')
        direccion_obj.ciudad = request.POST.get('ciudad')
        direccion_obj.pais = request.POST.get('pais')
        
        # Validación simple
        if not all([direccion_obj.calle, direccion_obj.codigo_postal, direccion_obj.colonia, direccion_obj.ciudad, direccion_obj.pais]):
             return redirect('tienda_mostrar_direccion') 

        try:
            # 4. Guardar en la Base de Datos
            direccion_obj.save()
            
            # Asignar al usuario si es nueva
            if not usuario.direccion:
                usuario.direccion = direccion_obj
                usuario.save()
            
            # =========================================================
            # AQUÍ ESTÁ LA MAGIA: REDIRECCIONAR AL PAGO
            # =========================================================
            return redirect('tienda_pago') 

        except Exception as e:
            print(f"Error al guardar dirección: {e}")
            return redirect('tienda_mostrar_direccion')

    # Si no es POST, recargamos la página
    return redirect('tienda_mostrar_direccion')

def tienda_confirmar_pedido(request):
    """Vista de ejemplo para el paso final del checkout."""
    return HttpResponse("¡Pedido Confirmado! Gracias por tu compra.")
# ==========================================================
# VISTAS DE CHECKOUT (PAGO Y CONFIRMACIÓN)
# ==========================================================

def tienda_pago(request):
    """Muestra la tarjeta guardada o el formulario para agregar una."""
    if not request.session.get('usuario_id'):
        return redirect('tienda_login')

    usuario = get_object_or_404(Usuario, pk=request.session['usuario_id'])
    cart_data = _get_cart_data(request)

    # Si el carrito está vacío, no debería estar aquí
    if cart_data['item_count'] == 0:
        return redirect('tienda_ver_carrito')

    context = {
        'titulo': 'Método de Pago',
        'usuario': usuario,
        'metodo_pago': usuario.metodo_pago, # Puede ser None o un objeto
        'cart_item_count': cart_data['item_count'],
        'total_general': cart_data['total_general'],
    }
    return render(request, 'tienda/checkout_pago.html', context)

def tienda_guardar_pago(request):
    """Procesa el formulario de pago y actualiza la tarjeta única del usuario."""
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=request.session['usuario_id'])
        
        titular = request.POST.get('titular')
        numero_tarjeta = request.POST.get('numero_tarjeta')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        cvv = request.POST.get('cvv')

        # Lógica: Si ya tiene método de pago, lo actualizamos. Si no, creamos uno.
        if usuario.metodo_pago:
            pago = usuario.metodo_pago
            pago.titular = titular
            pago.numero_tarjeta = numero_tarjeta
            pago.fecha_vencimiento = fecha_vencimiento
            pago.cvv = cvv
            pago.save()
        else:
            # Crear nuevo y asignar
            pago = MetodoPago.objects.create(
                titular=titular,
                numero_tarjeta=numero_tarjeta,
                fecha_vencimiento=fecha_vencimiento,
                cvv=cvv
            )
            usuario.metodo_pago = pago
            usuario.save()

        # Redirigir al Resumen Final
        return redirect('tienda_resumen_pedido')

    return redirect('tienda_pago')

def tienda_resumen_pedido(request):
    """Muestra el resumen final antes de confirmar la compra."""
    if not request.session.get('usuario_id'):
        return redirect('tienda_login')

    usuario = get_object_or_404(Usuario, pk=request.session['usuario_id'])
    cart_data = _get_cart_data(request)

    # Validaciones de seguridad
    if not usuario.direccion:
        return redirect('tienda_mostrar_direccion')
    if not usuario.metodo_pago:
        return redirect('tienda_pago')

    context = {
        'titulo': 'Resumen del Pedido',
        'usuario': usuario,
        'direccion': usuario.direccion,
        'metodo_pago': usuario.metodo_pago,
        'cart_items': cart_data['cart_items'],
        'total_general': cart_data['total_general'],
        'cart_item_count': cart_data['item_count'],
    }
    return render(request, 'tienda/checkout_resumen.html', context)

def tienda_finalizar_compra(request):
    """Guarda el Pedido y Detalles en la BD y limpia el carrito."""
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=request.session['usuario_id'])
        cart_data = _get_cart_data(request)
        
        if cart_data['item_count'] == 0:
             return redirect('tienda_index')

        # 1. Crear el objeto Pedido
        pedido = Pedido.objects.create(
            usuario=usuario,
            direccion_envio=usuario.direccion,
            metodo_pago=usuario.metodo_pago,
            total=cart_data['total_general'],
            estado='Pendiente'
        )

        # 2. Crear los DetallePedido (iterando el carrito)
        for item in cart_data['cart_items']:
            # Lógica para asignar el producto correcto según el tipo
            kw_args = {
                'pedido': pedido,
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario']
            }
            
            # Buscamos el objeto real en la BD para asignarlo a la FK correcta
            product_model = _get_product_model(item['type'])
            if product_model:
                producto_obj = product_model.objects.get(pk=item['id'])
                
                # Asignación dinámica: 'celular': obj, o 'laptop': obj...
                kw_args[item['type']] = producto_obj
                
                DetallePedido.objects.create(**kw_args)

        # 3. Limpiar el carrito de la sesión
        request.session['cart'] = {}
        request.session['cart_item_count'] = 0
        request.session.modified = True

        return render(request, 'tienda/gracias.html', {'pedido': pedido})

    return redirect('tienda_index')
# ==========================================================
# VISTAS CRUD DE PEDIDOS (FALTANTES)
# ==========================================================

def actualizar_pedido(request, pedido_id):
    """Permite cambiar el estado del pedido y ver sus detalles."""
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido)

    if request.method == 'POST':
        pedido.estado = request.POST.get('estado')
        pedido.save()
        # Al guardar, nos regresamos al perfil del usuario dueño del pedido
        return redirect('actualizar_usuario', usuario_id=pedido.usuario.id)

    context = {
        'pedido': pedido,
        'detalles': detalles,
        'titulo': 'Actualizar Estado del Pedido'
    }
    return render(request, 'crud/pedido/actualizar_pedido.html', context)

def borrar_pedido(request, pedido_id):
    """Borra un pedido individualmente."""
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    usuario_id = pedido.usuario.id # Guardamos el ID para volver
    
    if request.method == 'POST':
        pedido.delete()
        return redirect('actualizar_usuario', usuario_id=usuario_id)
        
    return render(request, 'crud/pedido/borrar_pedido.html', {'pedido': pedido})
# ... (otras importaciones)

def tienda_mis_pedidos(request):
    """Muestra el historial de pedidos del usuario logueado."""
    # 1. Verificar login
    if not request.session.get('usuario_id'):
        return redirect('tienda_login')
    
    # 2. Obtener usuario
    usuario = get_object_or_404(Usuario, pk=request.session['usuario_id'])
    
    # 3. Obtener sus pedidos (del más reciente al más antiguo)
    # Usamos prefetch_related o simplemente accedemos en el template al detalle_set si está configurado,
    # pero para simplificar, pasamos los pedidos y en el template iteramos.
    pedidos = Pedido.objects.filter(usuario=usuario).order_by('-fecha_pedido')
    
    # 4. Datos del carrito (para el navbar)
    cart_data = _get_cart_data(request)
    
    context = {
        'titulo': 'Mis Pedidos',
        'usuario': usuario,
        'pedidos': pedidos,
        'cart_item_count': cart_data['item_count']
    }
    return render(request, 'tienda/mis_pedidos.html', context)