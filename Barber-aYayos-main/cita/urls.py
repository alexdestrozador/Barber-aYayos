from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name='landing'),
    path('home/', views.home, name='home'),
    path('panel/admin/', views.panel_admin, name='panel_admin'),
    path('panel/', views.panel_control, name='panel_control'),
    path('perfil/perfil_administrador/', views.perfil_administrador, name='perfil_administrador'),
    
    
    
    path('finanzas/finanzas_admin/', views.finanzas_admin, name='finanzas_admin'),
    path('barbero/finanzas_barbero/', views.finanzas_barbero, name='finanzas_barbero'),
    path("finanzas/ajustar/<int:finanza_id>/", views.ajustar_comision, name="ajustar_comision"),

    path('citas/<int:cita_id>/eliminar/', views.eliminar_cita, name='eliminar_cita'),

    path("cita/historial_citas_admin/", views.historial_citas_admin, name="historial_citas_admin"),

    
  

    # 👥 Perfil cliente
    path('mi-cuenta/', views.perfil_cliente, name='perfil_cliente'),

   
    
    
    


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
    path("barbero/citas/", views.calendario_barbero, name="calendario_barbero"),
    path("api/citas-barbero/", views.citas_json_barbero, name="citas_json_barbero"),
    path("api/cita-completar/<int:cita_id>/", views.completar_cita, name="completar_cita"),
    path("horario/<int:barbero_id>/eliminar_todos/", views.eliminar_horarios_barbero, name="eliminar_horarios_barbero"),
    
    
   
 
    
    


    

    # 💈 Barberos
    path('barberos/nuevo/', views.nuevo_barbero, name='nuevo_barbero'),
    path('barberos/verificar-username/', views.verificar_username_barbero, name='verificar_username_barbero'),
    path('barberos/', views.lista_barberos, name='lista_barberos'),
    path('barberos/editar/<int:barbero_id>/', views.editar_barbero, name='editar_barbero'),
    path('barberos/eliminar/<int:barbero_id>/', views.eliminar_barbero, name='eliminar_barbero'),

    # 👨‍🏫 Módulo barbero
    path('barbero/panel/', views.panel_barbero, name='panel_barbero'),
    path('barbero/cambiar-estado/', views.cambiar_estado_barbero, name='cambiar_estado_barbero'),
    path("barbero/agregar-horario/", views.agregar_horario, name="agregar_horario"),
    

    path('ajax/horas-disponibles/', views.horas_disponibles, name='horas_disponibles'),
    path('barbero/perfil_barbero', views.perfil_barbero, name="perfil_barbero"),

    # 👥 Cliente - historial
    path('cliente/historial/', views.historial_citas_cliente, name='historial_citas_cliente'),
   
    path('ocultar-bienvenida/', views.ocultar_bienvenida, name='ocultar_bienvenida'),

    # 📅 Agendar cita
   
    path("agendar-nuevo/", views.agendar_cita_nuevo, name="agendar_cita_nuevo"),
    path("api/horarios/", views.horarios_disponibles, name="horarios_disponibles"),
    path('cita/<int:cita_id>/cancelar/', views.cancelar_cita, name='cancelar_cita'),

    # 👥 Clientes
    path('admin_clientes/', views.lista_clientes, name='lista_clientes'),
    path('admin_clientes/cambiar-estado/<int:cliente_id>/', views.cambiar_estado_cliente, name='cambiar_estado_cliente'),

    # 💰 Finanzas


    # ✅ Dashboard index (opcional)
    path('dashboard/', views.index_qs, name='index_qs'),

    # ✅ Admin de Django
    path('admin/', admin.site.urls),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
