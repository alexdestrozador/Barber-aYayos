from django.urls import path
from .import views 
urlpatterns = [
    
  path('', views.index, name='landing'),  # Esta es la que se carga al inicio

    # 🏠 Home o dashboard general
    path('home/', views.home, name='home'),

    # 👤 Paneles administrativos
    path('panel/admin/', views.panel_admin, name='panel_admin'),
    path('panel/', views.panel_control, name='panel_control'),
    
    
    
    path('perfil/perfil_administrador/', views.perfil_administrador, name= 'perfil_administrador'),

    # 📅 Citas
    path('citas/', views.lista_citas, name='lista_citas'),  # ← Renombrada para evitar conflicto
    path('citas/nueva/', views.nueva_cita, name='nueva_cita'),
    path('citas/editar/<int:cita_id>/', views.editar_cita, name='editar_cita'),
    path('citas/eliminar/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),

    # ✂️ Servicios
    path('servicios/', views.lista_servicios, name='lista_servicios'),
    path('servicios/nuevo/', views.nuevo_servicio, name='nuevo_servicio'),
    path('servicios/editar/<int:servicio_id>/', views.editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),

    # 🔐 Autenticación
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_cliente, name='registro_cliente'),
    path('logout/', views.logout_view, name='logout'),

    # 📄 Páginas informativas
    path('paginas/quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('paginas/contacto/', views.contacto, name='contacto'),

    # 🕒 Horarios
    path('horarios/', views.lista_horarios, name='lista_horarios'),
    path('horarios/nuevo/', views.nuevo_horario, name='nuevo_horario'),
    path('horarios/eliminar/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),

    # 💈 Barberos
    path('barberos/nuevo/', views.nuevo_barbero, name='nuevo_barbero'),
    path('barberos/verificar-username/', views.verificar_username_barbero, name='verificar_username_barbero'),
    path('barberos/', views.lista_barberos, name='lista_barberos'),
    path('barberos/editar/<int:barbero_id>/', views.editar_barbero, name='editar_barbero'),
    path('barberos/eliminar/<int:barbero_id>/', views.eliminar_barbero, name='eliminar_barbero'),

    # 👥 Clientes
    path('admin_clientes/', views.lista_clientes, name='lista_clientes'),
    path('admin_clientes/cambiar-estado/<int:cliente_id>/', views.cambiar_estado_cliente, name='cambiar_estado_cliente'),
   
    # 💰 Finanzas
    path('finanzas/ingresos/', views.reporte_ingresos, name='reporte_ingresos'),
    path('finanzas/barbero/', views.ingresos_por_barbero, name='ingresos_barbero'),
    path('finanzas/pagos/', views.pagos, name='pagos'),
    path('finanzas/comisiones/', views.configurar_comisiones, name='configurar_comisiones'),
    path('finanzas/comisiones/editar/<int:barbero_id>/', views.editar_comision, name='editar_comision'),

    # ✅ Vista opcional de dashboard index
    path('dashboard/', views.index_qs, name='index_qs'),  # Si la necesitas aparte
]
