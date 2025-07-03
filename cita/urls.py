from django.urls import path
from . import views

urlpatterns = [
    # 🏁 Landing page
    path('', views.index, name='landing'),

    # 🏠 Home / Paneles
    path('home/', views.home, name='home'),
    path('panel/', views.panel_control, name='panel_control'),
    path('panel/admin/', views.panel_admin, name='panel_admin'),
    path('perfil/perfil_administrador/', views.perfil_administrador, name='perfil_administrador'),

    # 🔐 Autenticación
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_cliente, name='registro_cliente'),
    path('logout/', views.logout_view, name='logout'),

    # ✂️ Servicios
    path('servicios/', views.lista_servicios, name='lista_servicios'),
    path('servicios/nuevo/', views.nuevo_servicio, name='nuevo_servicio'),
    path('servicios/editar/<int:servicio_id>/', views.editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),

    # 📅 Citas
    path('citas/', views.lista_citas, name='lista_citas'),
    path('citas/nueva/', views.nueva_cita, name='nueva_cita'),
    path('citas/editar/<int:cita_id>/', views.editar_cita, name='editar_cita'),
    path('citas/eliminar/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),

    # 🕒 Horarios
    path('horarios/', views.lista_horarios, name='lista_horarios'),
    path('horarios/nuevo/', views.nuevo_horario, name='nuevo_horario'),
    path('horarios/eliminar/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),

    # 💈 Barberos
    path('barberos/', views.lista_barberos, name='lista_barberos'),
    path('barberos/nuevo/', views.nuevo_barbero, name='nuevo_barbero'),
    path('barberos/editar/<int:barbero_id>/', views.editar_barbero, name='editar_barbero'),
    path('barberos/eliminar/<int:barbero_id>/', views.eliminar_barbero, name='eliminar_barbero'),
    path('barberos/verificar-username/', views.verificar_username_barbero, name='verificar_username_barbero'),

    # 👨‍🏫 Panel barbero
    path('barbero/panel/', views.panel_barbero, name='panel_barbero'),
    path('barbero/cambiar-estado/', views.cambiar_estado_barbero, name='cambiar_estado_barbero'),
    path('barbero/guardar-horarios/', views.guardar_horario_disponible, name='guardar_horario_disponible'),
    path('barbero/finanzas/', views.finanzas_barbero, name='finanzas_barbero'),
    path('barbero/citas/', views.citas_asignadas_barbero, name='citas_asignadas_barbero'),
    path('barbero/aceptar_cita/<int:cita_id>/', views.aceptar_cita, name='aceptar_cita'),
    path('barbero/rechazar_cita/<int:cita_id>/', views.rechazar_cita, name='rechazar_cita'),
    path('barbero/eliminar_cita/<int:cita_id>/', views.eliminar_cita_barbero, name='eliminar_cita_barbero'),

    # 👥 Clientes
    path('mi-cuenta/', views.perfil_cliente, name='perfil_cliente'),
    path('cliente/historial/', views.historial_citas_cliente, name='historial_citas_cliente'),
    path('cliente/eliminar_cita/<int:cita_id>/', views.eliminar_cita_cliente, name='eliminar_cita_cliente'),

    # 👥 Clientes - admin
    path('admin_clientes/', views.lista_clientes, name='lista_clientes'),
    path('admin_clientes/cambiar-estado/<int:cliente_id>/', views.cambiar_estado_cliente, name='cambiar_estado_cliente'),

    # 📄 Informativas
    path('paginas/quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('paginas/contacto/', views.contacto, name='contacto'),

    # 💰 Finanzas
    path('finanzas/ingresos/', views.reporte_ingresos, name='reporte_ingresos'),
    path('finanzas/barbero/', views.ingresos_por_barbero, name='ingresos_barbero'),
    path('finanzas/pagos/', views.pagos, name='pagos'),
    path('finanzas/comisiones/', views.configurar_comisiones, name='configurar_comisiones'),
    path('finanzas/comisiones/editar/<int:barbero_id>/', views.editar_comision, name='editar_comision'),

    # 📅 Agendar cita (cliente)
    path('agendar/', views.agendar_cita, name='agendar_cita'),

    # ⚡ AJAX
    path('ajax/horas-disponibles/', views.obtener_horas_disponibles, name='horas_disponibles'),

    # ✅ Dashboard / index alternativo
    path('dashboard/', views.index_qs, name='index_qs'),
]

