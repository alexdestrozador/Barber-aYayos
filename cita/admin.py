from django.contrib import admin
from .models import Cliente, Cita, Servicio, QuienesSomos




@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio', 'duracion')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)


admin.site.register(Cliente)
admin.site.register(Cita)

admin.site.register(QuienesSomos)

# Register your models here.
