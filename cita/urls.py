from django.urls import path
from . import views

urlpatterns = [
    
   path('landing/', views.index, name='landing'),


    path('home/', views.home, name='home'),
    

    path('panel/', views.panel_control, name='panel_control'),

    path('', views.lista_citas, name='lista_citas'),
    path('nueva/', views.nueva_cita, name='nueva_cita'),
    path('editar/<int:cita_id>/', views.editar_cita, name='editar_cita'),
    path('eliminar/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
    
    path('servicios/', views.lista_servicios, name='lista_servicios'),
    path('servicios/nuevo/', views.nuevo_servicio, name='nuevo_servicio'),
    path('servicios/editar/<int:servicio_id>/', views.editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),
    


path('paginas/quienes-somos/', views.quienes_somos, name='quienes_somos'),

   

   
path('paginas/', views.contacto, name='contacto'),

    path('horarios/', views.lista_horarios, name='lista_horarios'),
    path('horarios/nuevo/', views.nuevo_horario, name='nuevo_horario'),
    path('horarios/eliminar/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),
    
    path('barberos/nuevo/', views.nuevo_barbero, name='nuevo_barbero'),
path('barberos/verificar-username/', views.verificar_username_barbero, name='verificar_username_barbero'),
    path('barberos/', views.lista_barberos, name='lista_barberos'),
    path('barberos/editar/<int:barbero_id>/', views.editar_barbero, name='editar_barbero'),
    path('barberos/eliminar/<int:barbero_id>/', views.eliminar_barbero, name='eliminar_barbero'),
    
    

]
