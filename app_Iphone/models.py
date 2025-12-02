from django.db import models

# ==========================================================
# TABLA: Dirección
# ==========================================================
class Direccion(models.Model):
    calle = models.CharField(max_length=255)
    codigo_postal = models.CharField(max_length=10)
    colonia = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.calle}, {self.colonia}, {self.ciudad}, {self.pais}"

# ==========================================================
# TABLA: Método de Pago (NUEVA)
# ==========================================================
class MetodoPago(models.Model):
    titular = models.CharField(max_length=100)
    numero_tarjeta = models.CharField(max_length=16) # Guardar solo números
    fecha_vencimiento = models.CharField(max_length=5) # Formato MM/YY
    cvv = models.CharField(max_length=4)

    def __str__(self):
        # Muestra solo los últimos 4 dígitos por seguridad
        return f"Tarjeta que termina en {self.numero_tarjeta[-4:]} ({self.titular})"

# ==========================================================
# TABLA: Usuario (MODIFICADA)
# ==========================================================
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    contraseña = models.CharField(max_length=255)
    
    # Relaciones
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

# ==========================================================
# TABLA: Celulares
# ==========================================================
class Celular(models.Model):
    modelo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField()

    def __str__(self):
        return self.modelo

# ==========================================================
# TABLA: Laptops
# ==========================================================
class Laptop(models.Model):
    modelo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField()

    def __str__(self):
        return self.modelo

# ==========================================================
# TABLA: Tablets
# ==========================================================
class Tablet(models.Model):
    modelo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField()

    def __str__(self):
        return self.modelo

# ==========================================================
# TABLA: Airpods
# ==========================================================
class Airpod(models.Model):
    generacion = models.CharField(max_length=50)
    modelo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField()

    def __str__(self):
        return f"Airpods {self.generacion} - {self.modelo}"

# ==========================================================
# TABLA: Accesorios
# ==========================================================
class Accesorio(models.Model):
    tipo = models.CharField(max_length=100)
    modelo_compatible = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField()

    def __str__(self):
        return f"{self.tipo} ({self.modelo_compatible})"

# ==========================================================
# TABLA: Carrito
# ==========================================================
class Carrito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Carrito de {self.usuario.nombre}"

# ==========================================================
# TABLA: Items del Carrito
# ==========================================================
class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    
    celular = models.ForeignKey(Celular, null=True, blank=True, on_delete=models.SET_NULL)
    laptop = models.ForeignKey(Laptop, null=True, blank=True, on_delete=models.SET_NULL)
    tablet = models.ForeignKey(Tablet, null=True, blank=True, on_delete=models.SET_NULL)
    airpod = models.ForeignKey(Airpod, null=True, blank=True, on_delete=models.SET_NULL)
    accesorio = models.ForeignKey(Accesorio, null=True, blank=True, on_delete=models.SET_NULL)

    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Item en carrito de {self.carrito.usuario.nombre}"

# ==========================================================
# TABLA: Pedido (MODIFICADA)
# ==========================================================
class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)
    # Aquí conectamos el pedido con el método de pago usado
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, blank=True)
    
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, default="Pendiente")

    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario.nombre}"

# ==========================================================
# TABLA: Detalle del Pedido
# ==========================================================
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)

    celular = models.ForeignKey(Celular, null=True, blank=True, on_delete=models.SET_NULL)
    laptop = models.ForeignKey(Laptop, null=True, blank=True, on_delete=models.SET_NULL)
    tablet = models.ForeignKey(Tablet, null=True, blank=True, on_delete=models.SET_NULL)
    airpod = models.ForeignKey(Airpod, null=True, blank=True, on_delete=models.SET_NULL)
    accesorio = models.ForeignKey(Accesorio, null=True, blank=True, on_delete=models.SET_NULL)

    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle del pedido #{self.pedido.id}"