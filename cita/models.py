from django.db import models
from django.contrib.auth.models import User

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    correo = models.EmailField(max_length=254, blank=True, null=True)  # EmailField en vez de CharField

    def __str__(self):
        return self.user.username


class Cliente(models.Model):
    ESTADOS = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    telefono = models.CharField(max_length=15)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')  # 👈 nuevo campo
    activo = models.BooleanField(default=True) 

    def __str__(self):
        return self.user.get_full_name() if self.user else "Cliente sin usuario"


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.PositiveIntegerField(help_text="Duración en minutos")
    
    def __str__(self):
        return self.nombre


class Barbero(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    telefono = models.CharField(max_length=15)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() if self.user else "Barbero sin user"


class Cita(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    barbero = models.ForeignKey(Barbero, on_delete=models.SET_NULL, null=True)
    fecha_hora = models.DateTimeField()
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50, choices=[
        ('Pendiente', 'Pendiente'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('Completada', 'Completada'),
    ], default='Pendiente')

    def __str__(self):
        return f"{self.cliente.user.get_full_name() if self.cliente.user else 'Cliente sin usuario'} - {self.fecha_hora}"


class Horario(models.Model):
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE, related_name="horarios")
    dia = models.CharField(max_length=15, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado'),
        ('Domingo', 'Domingo'),
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.barbero.user.get_full_name() if self.barbero.user else 'Barbero sin usuario'} - {self.dia} de {self.hora_inicio} a {self.hora_fin}"


class QuienesSomos(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()

    def __str__(self):
        return self.titulo


class Comision(models.Model):
    barbero = models.OneToOneField(Barbero, on_delete=models.CASCADE)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje de comisión sobre el servicio")

    def __str__(self):
        return f"{self.barbero.user.get_full_name() if self.barbero.user else 'Barbero sin usuario'} - {self.porcentaje}%"


class Pago(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    fecha_pago = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pago de {self.cita} - {'Pagado' if self.pagado else 'Pendiente'}"

ESTADOS_CITA = [
    ('pendiente', 'Pendiente'),
    ('aceptada', 'Aceptada'),
    ('rechazada', 'Rechazada'),
]

class CitaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS_CITA, default='pendiente')

    visible_para_barbero = models.BooleanField(default=True)
    visible_para_cliente = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.cliente} - {self.servicio} ({self.estado})'

class HorarioDisponible(models.Model):
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()

    def __str__(self):
        return f"{self.fecha} - {self.hora} ({self.barbero})"