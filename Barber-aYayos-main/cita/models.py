from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.db.models import UniqueConstraint


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    correo = models.EmailField(max_length=254, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Cliente(models.Model):
    ESTADOS = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    telefono = models.CharField(max_length=15)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() if self.user else "Cliente sin usuario"


class Barbero(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    telefono = models.CharField(max_length=15)
    activo = models.BooleanField(default=True)
    comision = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=70.00,  # porcentaje que gana el barbero
        help_text="Porcentaje que gana el barbero (ej: 70 significa 70%)"
    )

    def __str__(self):
        return self.user.get_full_name() if self.user else "Barbero sin usuario"


class DiaLaboral(models.Model):
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE, related_name="dias_laborales")
    fecha = models.DateField()
    disponible = models.BooleanField(default=True)  # 🔹 nuevo campo

    class Meta:
        unique_together = ('barbero', 'fecha')
        ordering = ["fecha"]

    def __str__(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.barbero} - {self.fecha.strftime('%d/%m/%Y')} ({estado})"



class HorarioDisponible(models.Model):
    barbero = models.ForeignKey("Barbero", on_delete=models.CASCADE)
    dia_laboral = models.ForeignKey("DiaLaboral", on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    disponible = models.BooleanField(default=True)

    class Meta:
        ordering = ["fecha_hora"]

    def __str__(self):
        return f"{self.barbero} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.PositiveIntegerField(help_text="Duración en minutos")

    def __str__(self):
        return f"{self.nombre} - ${self.precio} ({self.duracion} min)"


class QuienesSomos(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()

    def __str__(self):
        return self.titulo



class Cita(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(Servicio)
    horario = models.ForeignKey(HorarioDisponible, on_delete=models.CASCADE)  # 🔹 ahora ForeignKey
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_pagado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ("confirmada", "Confirmada"),
            ("completada", "Completada"),
            ("cancelada", "Cancelada")
        ],
        default="confirmada"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cliente'],
                name='unique_cita_por_dia',
                condition=models.Q(estado__in=['confirmada', 'completada'])
            )
        ]

    def __str__(self):
        return f"{self.cliente} - {self.inicio.strftime('%d/%m/%Y %H:%M')} ({self.estado})"

    
    
class Finanza(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    ingreso_barbero = models.DecimalField(max_digits=10, decimal_places=2)
    ingreso_admin = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Finanza de cita {self.cita.id} - {self.barbero.user.get_full_name()}"


    def calcular_comisiones(self, porcentaje):
        self.porcentaje_comision = porcentaje
        self.comision_barbero = (self.monto_total * porcentaje) / 100
        self.ganancia_barberia = self.monto_total - self.comision_barbero
        self.ajustado = True
        self.save()

    def __str__(self):
        return f"Finanza - {self.barbero} - {self.cita.inicio.strftime('%d/%m/%Y')}"
    

    




