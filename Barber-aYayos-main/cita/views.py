import re
import json
import calendar
from decimal import Decimal
from collections import defaultdict
from datetime import datetime, date, time, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError
from django.db.models import Sum, ExpressionWrapper,F, DateTimeField, Func
from django.db.models.signals import post_save
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now
from django.utils.timezone import make_aware
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse



from .models import (
    Cita, Cliente, Servicio, DiaLaboral, HorarioDisponible, Barbero, QuienesSomos,
    Finanza, AdminProfile,
)
from .forms import PerfilAdminForm, BarberoPerfilForm

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)

def solo_superuser(usuario):
    return usuario.is_superuser



@login_required
def perfil_administrador(request):
    perfil, _ = AdminProfile.objects.get_or_create(user=request.user)
    error_password = None  # Para mostrar error debajo del formulario

    if request.method == 'POST':
        form = PerfilAdminForm(request.POST, request.FILES, instance=perfil)
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if form.is_valid():
            perfil.save()

            # Cambio de contraseña
            if password and password2:
                if password == password2:
                    request.user.set_password(password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # ⚡ mantiene la sesión
                    messages.success(request, 'Contraseña cambiada con éxito.')
                else:
                    error_password = 'Las contraseñas no coinciden.'

            # Mensaje de perfil actualizado (si no hay error de contraseña)
            if not error_password:
                messages.success(request, 'Perfil actualizado con éxito.')
                
            return redirect('perfil_administrador')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = PerfilAdminForm(instance=perfil)

    return render(request, 'perfil/perfil_administrador.html', {
        'form': form,
        'error_password': error_password
    })



@login_required
def perfil_barbero(request):
    # Obtiene o crea el perfil del barbero
    barbero, _ = Barbero.objects.get_or_create(user=request.user)
    error_password = None

    if request.method == 'POST':
        form = BarberoPerfilForm(request.POST, instance=barbero, user=request.user)
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if form.is_valid():
            # ✅ Primero actualiza el barbero
            form.save()

            # ✅ Actualiza el usuario
            user = request.user
            user.first_name = form.cleaned_data.get("first_name")
            user.username = form.cleaned_data.get("username")

            # ✅ Cambio de contraseña
            if password and password2:
                if password == password2:
                    user.set_password(password)
                    user.save()
                    update_session_auth_hash(request, user)  # mantiene sesión
                    messages.success(request, "Contraseña cambiada con éxito ✅")
                else:
                    error_password = "Las contraseñas no coinciden ❌"
                    messages.warning(request, error_password)
                    return redirect("perfil_barbero")

            user.save()

            # Solo muestra success si no hubo error de contraseña
            if not error_password:
                messages.success(request, "Perfil actualizado correctamente ✅")

            return redirect("perfil_barbero")

        else:
            # ❌ Solo entra aquí cuando el formulario tiene errores
            messages.warning(request, "Por favor corrige los errores ⚠️")
            return redirect("perfil_barbero")

    else:
        form = BarberoPerfilForm(instance=barbero, user=request.user)

    return render(request, "barbero/perfil_barbero.html", {
        "form": form,
        "error_password": error_password
    })







@user_passes_test(solo_superuser, login_url="/")
def panel_admin(request):
    return render(request, 'Home/home.html')


def index(request):
    return render(request, 'Landing/index.html')

def home(request):
    return render(request, 'Home/home.html')

def quienes_somos(request, pk):
    seccion = get_object_or_404(QuienesSomos, pk=pk)

    if request.method == 'POST':
        seccion.titulo = request.POST.get('titulo')
        seccion.descripcion  = request.POST.get('descripcion')
        seccion.save()
        messages.success(request, "Sección actualizada correctamente.")
        return redirect('quienes_somos', pk=seccion.pk)

    return render(request, 'paginas/quienes_somos.html', {'seccion': seccion})

    context = {'seccion': seccion}
    return render(request, 'quienes_somos.html', context)

def contacto(request):
    return render(request, 'paginas/contacto.html')

def login_view(request):
    
    storage = messages.get_messages(request)
    storage.used = True 
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            # Si es barbero
            try:
                barbero = Barbero.objects.get(user=user)
                request.session['usuario'] = barbero.user.username
                request.session['tipo'] = 'barbero'
                return redirect('panel_barbero')
            except Barbero.DoesNotExist:
                pass

            # Si es cliente
            try:
                cliente = Cliente.objects.get(user=user)
                if not cliente.activo:
                    messages.error(request, "Cuenta inactiva.", extra_tags="auth")
                    return redirect('login')
                request.session['usuario'] = cliente.user.username
                request.session['tipo'] = 'cliente'
                return redirect('perfil_cliente')
            except Cliente.DoesNotExist:
                pass

            # Si es administrador
            if user.is_superuser:
                return redirect('panel_admin')

        messages.error(request, "Credenciales inválidas", extra_tags="auth")

    return render(request, 'Landing/login.html')


def registro_cliente(request):
    
    storage = messages.get_messages(request)
    storage.used = True 
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        password = request.POST.get('password', '').strip()
        confirmar_password = request.POST.get('confirmar_password', '').strip()

        errores_generales = []
        error_password = None

        # Validaciones
        if not all([username, nombre, correo, telefono, password, confirmar_password]):
            errores_generales.append("Todos los campos son obligatorios.")

        if password != confirmar_password:
            error_password = "Las contraseñas no coinciden."

        if User.objects.filter(username=username).exists():
            errores_generales.append("El nombre de usuario ya está registrado.")

        if User.objects.filter(email=correo).exists():
            errores_generales.append("El correo electrónico ya está en uso.")

        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
        if not re.match(password_regex, password):
            errores_generales.append(
                "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y símbolos."
            )

        if errores_generales or error_password:
            return render(request, 'Landing/login.html', {
                'form_type': 'register',
                'username': username,
                'nombre': nombre,
                'correo': correo,
                'telefono': telefono,
                'errores_generales': errores_generales,
                'error_password': error_password,
            })

        # Crear el usuario y autenticar
        try:
            user = User.objects.create_user(
                username=username,
                email=correo,
                password=password,
                first_name=nombre
            )

            Cliente.objects.create(
                user=user,
                telefono=telefono,
                activo=True
            )


            login(request, user)
            request.session['primer_ingreso'] = True  # Marca que acaba de registrarse
            return redirect('perfil_cliente')  # Asegúrate de tener esta URL definida

        except IntegrityError:
            return render(request, 'Landing/login.html', {
                'form_type': 'register',
                'username': username,
                'nombre': nombre,
                'correo': correo,
                'telefono': telefono,
                'errores_generales': ["Error al crear el usuario. Intenta con otro correo o usuario."],
            })

    return redirect('login')

@csrf_exempt
def ocultar_bienvenida(request):
    if request.method == 'POST':
        request.session.pop('primer_ingreso', None)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'denied'}, status=405)



        


def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'admin_clientes/lista_clientes.html', {'clientes': clientes})

def cambiar_estado_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.estado = 'inactivo' if cliente.estado == 'activo' else 'activo'
    cliente.save()
    return redirect('lista_clientes')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def cliente_dashboard(request):
    return HttpResponse(f"Bienvenido cliente {request.session.get('usuario')}")

def barbero_dashboard(request):
    return HttpResponse(f"Bienvenido barbero {request.session.get('usuario')}")

def panel_control(request):
    num_barberos = Barbero.objects.count()
    num_servicios = Servicio.objects.count()
    num_citas = Cita.objects.count()
    num_clientes = Cliente.objects.count()


    context = {
        'num_barberos': num_barberos,
        'num_servicios': num_servicios,
        'num_citas': num_citas,
        'num_clientes': num_clientes,
        
    }
    return render(request, 'cita/panel_control.html', context)

@login_required
def reporte_finanzas(request):
    finanzas = Finanza.objects.select_related("barbero", "cita")

    total_general = finanzas.aggregate(total=Sum("monto_total"))["total"] or 0
    total_comisiones = finanzas.aggregate(total=Sum("comision_barbero"))["total"] or 0
    total_barberia = finanzas.aggregate(total=Sum("ganancia_barberia"))["total"] or 0

    ingresos_por_barbero = (
        finanzas.values("barbero__user__first_name", "barbero__user__last_name")
        .annotate(
            total=Sum("monto_total"),
            comision=Sum("comision_barbero"),
            ganancia=Sum("ganancia_barberia"),
        )
    )

    return render(request, "finanzas/reporte.html", {
        "finanzas": finanzas,
        "total_general": total_general,
        "total_comisiones": total_comisiones,
        "total_barberia": total_barberia,
        "ingresos_por_barbero": ingresos_por_barbero,
    })


@login_required


def lista_servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'servicio/lista_servicios.html', {'servicios': servicios})

def nuevo_servicio(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        duracion = request.POST.get('duracion')

        errores = {}

        if not nombre:
            errores['nombre'] = "Llena este campo. ¡Recuerda que el * señala que es un campo obligatorio!"
        if not precio:
            errores['precio'] = "Llena este campo. ¡Recuerda que el * señala que es un campo obligatorio!"
        if not duracion:
            errores['duracion'] = "Llena este campo. ¡Recuerda que el * señala que es un campo obligatorio!"

        if errores:
            return render(request, 'servicio/nuevo_servicio.html', {
                'errores': errores,
                'form_data': {
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'precio': precio,
                    'duracion': duracion
                }
            })

        Servicio.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            duracion=duracion
        )
        messages.success(request, '¡Servicio agregado exitosamente!')
        return redirect('nuevo_servicio')

    return render(request, 'servicio/nuevo_servicio.html')

def editar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == 'POST':
        servicio.nombre = request.POST.get('nombre')
        servicio.descripcion = request.POST.get('descripcion')
        servicio.precio = request.POST.get('precio')
        servicio.duracion = request.POST.get('duracion')
        servicio.save()

        messages.success(request, "Servicio actualizado")
        return redirect('lista_servicios')

    return render(request, 'servicio/editar_servicio.html', {'servicio': servicio})

def eliminar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    servicio.delete()
    return redirect('lista_servicios')

def asignar_dias_laborales(request):
    barberos = Barbero.objects.all()
    dias = DiaLaboral.DIAS_SEMANA

    if request.method == "POST":
        barbero_id = request.POST.get("barbero_id")
        dias_seleccionados = request.POST.getlist("dias")

        barbero = get_object_or_404(Barbero, id=barbero_id)

        for dia in dias_seleccionados:
            if DiaLaboral.objects.filter(barbero=barbero, dia=dia).exists():
                messages.warning(request, f"⚠️ El día {dia} ya estaba asignado a {barbero.user.get_full_name()}.")
            else:
                DiaLaboral.objects.create(barbero=barbero, dia=dia)
                messages.success(request, f"✅ Día {dia} asignado a {barbero.user.get_full_name()}.")

        return redirect("lista_dias_laborales")

    return render(request, "horario/asignar_dias.html", {
        "barberos": barberos,
        "dias": dias
    })

    
    
    
@login_required
def lista_horarios(request):
    barberos_con_horarios = {}

    for barbero in Barbero.objects.all():
        # Cambiamos 'dia' por 'fecha'
        dias = DiaLaboral.objects.filter(barbero=barbero).values_list("fecha", flat=True)

        if dias.exists():
            # Formateamos las fechas para que sean legibles
            dias_formateados = [d.strftime("%d/%m/%Y") for d in dias]
            barberos_con_horarios[barbero] = dias_formateados

    return render(request, "horario/lista_horarios.html", {
        "barberos_con_horarios": barberos_con_horarios
    })


def nuevo_barbero(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        username = request.POST.get('username', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('email', '').strip()
        password_raw = request.POST.get('password', '').strip()

        if nombre and username and telefono and correo and password_raw:
            if User.objects.filter(username=username).exists():
                return render(request, 'admin_barbero/nuevo_barbero.html', {
                    'error': 'El nombre de usuario ya está en uso.',
                    'form_data': request.POST
                })

            try:
                # Crear el usuario
                user = User.objects.create_user(
                    username=username,
                    password=password_raw,
                    email=correo,
                    first_name=nombre
                )

                # Crear el barbero y asociarlo al usuario
                Barbero.objects.create(
                    user=user,
                    telefono=telefono
                )

                # ✅ Mensaje de éxito
                messages.success(request, f"El barbero {nombre} fue agregado correctamente.")

                return redirect('lista_barberos')

            except Exception as e:
                return render(request, 'admin_barbero/nuevo_barbero.html', {
                    'error': str(e),
                    'form_data': request.POST
                })
        else:
            return render(request, 'admin_barbero/nuevo_barbero.html', {
                'error': 'Todos los campos son obligatorios.',
                'form_data': request.POST
            })

    return render(request, 'admin_barbero/nuevo_barbero.html')


def verificar_username_barbero(request):
    username = request.GET.get('username', '').strip()
    barbero_id = request.GET.get('barbero_id')

    if barbero_id:
        barbero = get_object_or_404(Barbero, id=barbero_id)
        existe = User.objects.filter(username__iexact=username).exclude(id=barbero.user.id).exists()
    else:
        existe = User.objects.filter(username__iexact=username).exists()

    return JsonResponse({'existe': existe})

def lista_barberos(request):
    barberos = Barbero.objects.all()
    return render(request, 'admin_barbero/lista_barberos.html', {'barberos': barberos})

def editar_barbero(request, barbero_id):
    barbero = get_object_or_404(Barbero, id=barbero_id)
    user = barbero.user

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        username = request.POST.get('username', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()

        if nombre and username and telefono and email:
            if User.objects.filter(username__iexact=username).exclude(id=user.id).exists():
                return render(request, 'admin_barbero/editar_barbero.html', {
                    'barbero': barbero,
                    'error': 'El nombre de usuario ya está en uso.'
                })

            try:
                user.first_name = nombre
                user.username = username
                user.email = email
                user.save()

                barbero.telefono = telefono
                barbero.save()

                # ✅ Mensaje de éxito
                messages.success(request, 'Barbero editado correctamente.')
                return redirect('lista_barberos')

            except Exception as e:
                return render(request, 'admin_barbero/editar_barbero.html', {
                    'barbero': barbero,
                    'error': str(e)
                })

        else:
            return render(request, 'admin_barbero/editar_barbero.html', {
                'barbero': barbero,
                'error': 'Todos los campos son obligatorios.'
            })

    return render(request, 'admin_barbero/editar_barbero.html', {'barbero': barbero})

def eliminar_barbero(request, barbero_id):
    barbero = get_object_or_404(Barbero, id=barbero_id)
    barbero.delete()
    return redirect('lista_barberos')

def index(request):
    quienes_somos = QuienesSomos.objects.first()
    return render(request, 'Landing/index.html', {
        'quienes_somos': quienes_somos
    })


def quienes_somos(request):
    seccion, created = QuienesSomos.objects.get_or_create(id=1)

    if request.method == 'POST':
        seccion.titulo = request.POST.get('titulo')
        seccion.descripcion = request.POST.get('descripcion')
        seccion.save()

        url = reverse('quienes_somos')  # obtienes URL con nombre
        url = f'{url}?updated=1'         # agregas el parámetro GET
        return HttpResponseRedirect(url) # rediriges con el parámetro

    update_success = request.GET.get('updated') == '1'
    
    return render(request, 'paginas/quienes_somos.html', {
        'seccion': seccion,
        'update_success': update_success
    })



def index_qs(request):
    contenido = QuienesSomos.objects.all()
    return render(request, 'Landing/index.html', {'contenido': contenido})

    #modelcliente
    
@login_required
def perfil_cliente(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, "No eres cliente.")
        return redirect("login")

    # Trae solo las citas activas (no canceladas)
    citas = (
        Cita.objects.filter(cliente=cliente)
        .exclude(estado="cancelada")
        .select_related("barbero", "horario")
        .prefetch_related("servicios")
        .order_by("horario__fecha_hora")
    )

    # Conteos para resumen
    completadas_count = citas.filter(estado="completada").count()
    proxima_cita = citas.filter(inicio__gte=timezone.now(), estado="confirmada").first()

    # Hora actual para comparación de cancelaciones
    ahora = timezone.now()

    return render(request, "cliente/perfil_cliente.html", {
        "cliente": cliente,
        "citas": citas,
        "completadas_count": completadas_count,
        "proxima_cita": proxima_cita,
        "ahora": ahora,  # <-- lo usas en el template para deshabilitar el botón
    })










@login_required

def cambiar_estado_barbero(request):
    barbero = request.user.barbero
    if request.method == 'POST':
        barbero.activo = not barbero.activo
        barbero.save()

        estado = "Activo" if barbero.activo else "Descanso"
        messages.success(request, f"Su estado ha sido cambiado a {estado}")

    return render(request, 'barbero/estado_barbero.html', {'barbero': barbero})





@login_required
def agregar_horario(request):
    barbero = request.user.barbero
    dias_laborales = DiaLaboral.objects.filter(barbero=barbero).order_by("fecha")

    if request.method == "POST":
        dia_id = request.POST.get("dia_laboral")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")

        # Validación 0: campos completos
        if not dia_id or not hora_inicio or not hora_fin:
            messages.error(request, "Debes completar todos los campos.")
            return redirect("agregar_horario")

        hora_ini = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin_dt = datetime.strptime(hora_fin, "%H:%M").time()

        # Validación 1: hora de inicio < hora fin
        if hora_ini >= hora_fin_dt:
            messages.error(request, "La hora de inicio debe ser menor a la de fin.")
            return redirect("agregar_horario")

        # Validación 2: dentro del horario de atención (08:00 a 20:00)
        if hora_ini < time(8, 0) or hora_fin_dt > time(20, 0):
            messages.error(request, "Las horas deben estar dentro del horario de atención: 08:00-20:00")
            return redirect("agregar_horario")

        dia = DiaLaboral.objects.get(id=dia_id)

        # Validación 3: la fecha no está en el pasado
        if dia.fecha < timezone.now().date():
            messages.error(request, "No puedes asignar horarios para fechas pasadas.")
            return redirect("agregar_horario")

        # Crear intervalos de 1 hora
        actual = timezone.make_aware(datetime.combine(dia.fecha, hora_ini))
        fin = timezone.make_aware(datetime.combine(dia.fecha, hora_fin_dt))

        while actual < fin:
            # Validación 4: evitar solapamientos
            if HorarioDisponible.objects.filter(dia_laboral=dia, fecha_hora=actual).exists():
                actual += timedelta(hours=1)
                continue

            # Validación 5: evitar horarios pasados
            if actual < timezone.now():
                actual += timedelta(hours=1)
                continue

            HorarioDisponible.objects.create(
                barbero=barbero,
                dia_laboral=dia,
                fecha_hora=actual,
                disponible=True
            )
            actual += timedelta(hours=1)

        messages.success(request, "Horario agregado con éxito.")
        return redirect("agregar_horario")

    # Mostrar horarios existentes
    horarios = HorarioDisponible.objects.filter(barbero=barbero)

    return render(request, "barbero/agregar_horario.html", {
        "dias_laborales": dias_laborales,
        "horarios": horarios,
    })




    
@login_required
def historial_citas_cliente(request):
    cliente = request.user.cliente  # Asumiendo que tu modelo Cliente tiene relación OneToOne con User
    citas = Cita.objects.filter(cliente=cliente).order_by('-fecha_hora')
    return render(request, 'cliente/historial_citas.html', {
        'citas': citas
    })








   










@login_required
def nuevo_horario(request):
    barberos = Barbero.objects.all()
    if request.method == "POST":
        barbero_id = request.POST.get("barbero_id")
        fechas_str = request.POST.get("fechas")  # ej: "2025-09-15,2025-09-16"
        fechas = [f.strip() for f in fechas_str.split(",") if f.strip()]

        if not barbero_id or not fechas:
            messages.error(request, "Debes seleccionar barbero y al menos una fecha")
            return redirect("nuevo_horario")

        barbero = Barbero.objects.get(id=barbero_id)
        errores = []

        for fecha_str in fechas:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

            # Validación 1: No asignar días pasados
            if fecha < datetime.today().date():
                errores.append(f"No se puede asignar {fecha} porque es un día pasado.")
                continue

            # Validación 2: Evitar duplicados (ya lo protege unique_together)
            if DiaLaboral.objects.filter(barbero=barbero, fecha=fecha).exists():
                errores.append(f"El día {fecha} ya está asignado.")
                continue

            # Crear el día laboral válido
            DiaLaboral.objects.create(barbero=barbero, fecha=fecha)

        if errores:
            for e in errores:
                messages.error(request, e)
        else:
            messages.success(request, "Días asignados correctamente")

        return redirect("lista_horarios")

    return render(request, "horario/nuevo_horario.html", {"barberos": barberos})








    
@login_required
def panel_barbero(request):
    try:
        barbero = Barbero.objects.get(user=request.user)  # ✅ Instancia de Barbero
    except Barbero.DoesNotExist:
        messages.error(request, "No sos barbero.")
        return redirect('login')

    hoy = date.today()

    # ✅ Citas ordenadas por fecha y hora (relación con HorarioDisponible)
    citas = (
        Cita.objects.filter(barbero=barbero)
        .select_related("cliente", "horario", "servicio")
        .order_by("horario__fecha_hora")
    )

    # ✅ Ingresos de hoy (filtramos por el horario__fecha_hora)


    # ✅ Horarios disponibles del barbero
    horarios = HorarioDisponible.objects.filter(barbero=barbero).order_by("fecha_hora")

    context = {
        "barbero": barbero,
        "citas": citas,
        "hoy": hoy,
        "horarios": horarios,
    }
    return render(request, "barbero/panel_barbero.html", context)


@login_required
def horas_disponibles(request, barbero_id):
    fecha = request.GET.get("fecha")
    horarios = HorarioDisponible.objects.filter(
        barbero_id=barbero_id,
        fecha=fecha,
        disponible=True
    ).order_by("hora")

    data = [{"id": h.id, "hora": h.hora.strftime("%H:%M")} for h in horarios]
    return JsonResponse(data, safe=False)

    
    
@login_required
def calendario_barbero(request):
    return render(request, "barbero/calendario.html")

@login_required
def citas_json_barbero(request):
    try:
        barbero = request.user.barbero
    except Barbero.DoesNotExist:
        return JsonResponse([], safe=False)

    citas = Cita.objects.filter(
        barbero=barbero,
        estado__in=["confirmada", "completada"]
    )

    data = []
    for cita in citas:
        # 👇 Convertimos inicio y fin a hora local
        inicio_local = timezone.localtime(cita.inicio)
        fin_local = timezone.localtime(cita.fin)

        data.append({
            "id": cita.id,
            "title": f"{cita.cliente.user.first_name} - {', '.join(s.nombre for s in cita.servicios.all())}",
            "start": inicio_local.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": fin_local.strftime("%Y-%m-%dT%H:%M:%S"),
            "color": "#28a745" if cita.estado == "completada" else "#007bff",
        })

    return JsonResponse(data, safe=False)




@login_required
@require_POST
def completar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    # Marcar como completada
    cita.estado = "completada"
    cita.save()

    return JsonResponse({"success": True})




@require_POST
def ajustar_comision(request, finanza_id):
    finanza = get_object_or_404(Finanza, id=finanza_id)

    try:
        porcentaje = float(request.POST.get("porcentaje", 0))
    except ValueError:
        messages.error(request, "El porcentaje ingresado no es válido.")
        return redirect("finanzas_admin")

    if porcentaje < 0 or porcentaje > 100:
        messages.error(request, "El porcentaje debe estar entre 0 y 100.")
        return redirect("finanzas_admin")

    # Usamos el método que ya tienes en el modelo Finanza
    finanza.calcular_comisiones(porcentaje)

    messages.success(request, f"Comisión ajustada correctamente para la cita {finanza.cita.id}.")
    return redirect("finanzas_admin")


@login_required
def finanzas_barbero(request):
    barbero = request.user.barbero
    mes_actual = now().month
    finanzas = barbero.finanzas.filter(fecha_registro__month=mes_actual, ajustado=True)

    total_mes = finanzas.aggregate(Sum("comision_barbero"))["comision_barbero__sum"] or 0

    return render(request, "barbero/finanzas_barbero.html", {
        "finanzas": finanzas,
        "total_mes": total_mes
    })

@login_required
def finanzas_admin(request):
    mes_actual = now().month
    finanzas = Finanza.objects.filter(fecha_registro__month=mes_actual, ajustado=True)

    resumen = finanzas.values("barbero__user__first_name", "barbero__user__last_name") \
        .annotate(
            total_barbero=Sum("comision_barbero"),
            total_barberia=Sum("ganancia_barberia")
        )

    return render(request, "finanzas/finanzas_admin.html", {
        "finanzas": finanzas,
        "resumen": resumen
    })




@login_required
def agendar_cita_nuevo(request):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, "Solo los clientes pueden agendar citas.")
        return redirect("home")

    if request.method == "POST":
        servicios_ids = request.POST.getlist("servicios")
        barbero_id = request.POST.get("barbero")
        fecha_hora_id = request.POST.get("fecha_hora")

        if not (servicios_ids and barbero_id and fecha_hora_id):
            messages.error(request, "Por favor completa todos los campos.")
            return redirect("agendar_cita_nuevo")

        barbero = get_object_or_404(Barbero, id=barbero_id)

        # ✅ Solo horarios disponibles
        horario = HorarioDisponible.objects.filter(
            id=fecha_hora_id,
            disponible=True,
            barbero=barbero
        ).first()

        if not horario:
            messages.error(request, "Ese horario ya fue tomado, elige otro.")
            return redirect("agendar_cita_nuevo")

        # ✅ Validar que el cliente no tenga otra cita confirmada/completada ese día
        fecha_cita = horario.fecha_hora.date()
        if Cita.objects.filter(
            cliente=cliente,
            inicio__date=fecha_cita,
            estado__in=["confirmada", "completada"]
        ).exists():
            messages.error(request, "Ya tienes una cita ese día.")
            return redirect("agendar_cita_nuevo")

        servicios = Servicio.objects.filter(id__in=servicios_ids)
        total_precio = sum(s.precio for s in servicios)
        total_duracion = sum(s.duracion for s in servicios)

        # ✅ Crear la cita
        cita = Cita.objects.create(
            cliente=cliente,
            barbero=barbero,
            horario=horario,  # ahora es ForeignKey, se puede reutilizar
            inicio=horario.fecha_hora,
            fin=horario.fecha_hora + timedelta(minutes=total_duracion),
            precio_total=total_precio,
            estado="confirmada"
        )
        cita.servicios.set(servicios)

        # ✅ Marcar horario como ocupado
        horario.disponible = False
        horario.save(update_fields=["disponible"])

        # 🔔 Redirigir con parámetro para SweetAlert
        return redirect(f"{reverse('perfil_cliente')}?agendada=1")

    servicios = Servicio.objects.all()
    barberos = Barbero.objects.all()
    return render(request, "cliente/agendar_cita_nuevo.html", {
        "servicios": servicios,
        "barberos": barberos,
    })


    
@login_required
def cancelar_cita(request, cita_id):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, "No eres cliente.")
        return redirect("home")

    cita = get_object_or_404(Cita, id=cita_id, cliente=cliente)

    # 🚫 Ya no se puede cancelar si está cancelada o completada
    if cita.estado in ["cancelada", "completada"]:
        messages.warning(request, "Esta cita ya no se puede cancelar.")
        return redirect("perfil_cliente")

    ahora = timezone.now()
    if cita.inicio - ahora < timedelta(hours=2):
        messages.error(request, "Solo puedes cancelar hasta 2 horas antes.")
        return redirect("perfil_cliente")

    # ❌ Cambiar estado
    cita.estado = "cancelada"
    cita.save(update_fields=["estado"])

    # 🔓 Liberar el horario para que quede disponible otra vez
    if cita.horario:
        cita.horario.disponible = True
        cita.horario.save(update_fields=["disponible"])

    # 🔔 Redirigir con parámetro para SweetAlert
    return redirect(f"{reverse('perfil_cliente')}?cancelada=1")


@staff_member_required
def historial_citas_admin(request):
    # Traer TODAS las citas con detalles
    citas = (
        Cita.objects
        .select_related("cliente__user", "barbero__user")
        .prefetch_related("servicios")
        .order_by("-inicio")
    )

    return render(request, "cita/historial_citas_admin.html", {
        "citas": citas,
    })


@login_required
def eliminar_cita(request, cita_id):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, "No eres cliente.")
        return redirect("home")

    try:
        cita = Cita.objects.get(id=cita_id, cliente=cliente)
    except Cita.DoesNotExist:
        messages.error(request, f"No se encontró la cita con id={cita_id} para este cliente.")
        return redirect("perfil_cliente")

    if cita.estado != "completada":
        messages.warning(request, "Solo puedes eliminar citas completadas.")
        return redirect("perfil_cliente")

    cita.delete()
    messages.success(request, "La cita ha sido eliminada correctamente.")
    return redirect("perfil_cliente")


@login_required
def horarios_disponibles(request):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        return JsonResponse([], safe=False)

    barbero_id = request.GET.get("barbero")
    servicios_ids = request.GET.getlist("servicios[]")

    if not barbero_id or not servicios_ids:
        return JsonResponse([], safe=False)

    servicios = Servicio.objects.filter(id__in=servicios_ids)
    total_duracion = sum(s.duracion for s in servicios)

    horarios = HorarioDisponible.objects.filter(
        barbero_id=barbero_id,
        disponible=True
    ).order_by("fecha_hora")

    # días donde el cliente ya tiene citas confirmadas o completadas
    dias_ocupados = set(
        Cita.objects.filter(
            cliente=cliente,
            estado__in=["confirmada", "completada"]
        ).values_list("inicio__date", flat=True)
    )

    hoy = date.today()
    data = []

    for h in horarios:
        inicio = h.fecha_hora
        fin = inicio + timedelta(minutes=total_duracion)

        choque = Cita.objects.filter(
            barbero_id=barbero_id,
            inicio__lt=fin,
            fin__gt=inicio,
            estado__in=["confirmada", "completada"]
        ).exists()

        # ❌ no permitir mismo día si ya tuvo una confirmada o completada
        if choque or inicio.date() in dias_ocupados:
            continue

        # ❌ opcional: bloquear horarios para hoy
        if inicio.date() == hoy:
            continue

        data.append({
            "id": h.id,
            "fecha": inicio.strftime("%d/%m/%Y"),
            "hora": inicio.strftime("%H:%M"),
            "texto": inicio.strftime("%d/%m/%Y %H:%M")
        })

    return JsonResponse(data, safe=False)

@login_required
def eliminar_horarios_barbero(request, barbero_id):
    barbero = get_object_or_404(Barbero, id=barbero_id)
    
    # Eliminar todos los días laborales de este barbero
    DiaLaboral.objects.filter(barbero=barbero).delete()

    # Mensaje con etiqueta "eliminacion"
    messages.success(
        request,
        f"Se eliminaron todos los horarios de {barbero.user.get_full_name()}",
        extra_tags="eliminacion"
    )
    
    return redirect("lista_horarios")
