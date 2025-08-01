from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cita, Cliente, Servicio, Horario, Barbero, QuienesSomos, Pago, Comision, HorarioDisponible, CitaCliente
from datetime import datetime
from django.utils.timezone import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import PerfilAdminForm
from .models import AdminProfile
from collections import defaultdict
import calendar
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, date, time
import json


def solo_superuser(usuario):
    return usuario.is_superuser

@login_required
def perfil_administrador(request):
    perfil, _ = AdminProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PerfilAdminForm(request.POST, request.FILES, instance=perfil)
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if form.is_valid():
            form.save()

            if password and password2:
                if password == password2:
                    user = request.user
                    user.set_password(password)
                    user.save()
                    messages.success(request, 'La contraseña ha sido actualizada.')
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return redirect('perfil_administrador')

            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil_administrador')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = PerfilAdminForm(instance=perfil)

    return render(request, 'perfil/perfil_administrador.html', {'form': form})


@user_passes_test(solo_superuser, login_url="/")
def panel_admin(request):
    return render(request, 'Home/home.html')


def holamundo(request):
    return render(request, 'Landing/holamundo.html')

def home(request):
    return render(request, 'Home/home.html')

def quienes_somos(request):
    seccion, _ = QuienesSomos.objects.get_or_create(id=1)

    if request.method == 'POST':
        seccion.titulo = request.POST.get('titulo')
        seccion.descripcion = request.POST.get('descripcion')
        seccion.save()
        return redirect('index')

    return render(request, 'paginas/quienes_somos.html', {'seccion': seccion})

def contacto(request):
    return render(request, 'paginas/contacto.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Verificar si es barbero
            if Barbero.objects.filter(user=user).exists():
                request.session['usuario'] = user.username
                request.session['tipo'] = 'barbero'
                return redirect('panel_barbero')

            # Verificar si es cliente
            elif Cliente.objects.filter(user=user).exists():
                cliente = Cliente.objects.get(user=user)
                if not cliente.activo:
                    messages.error(request, "Cuenta inactiva.")
                    return redirect('login')

                request.session['usuario'] = user.username
                request.session['tipo'] = 'cliente'
                return redirect('perfil_cliente')

            # Verificar si es administrador
            elif user.is_superuser:
                request.session['usuario'] = user.username
                request.session['tipo'] = 'admin'
                return redirect('panel_admin')

        # Si no se autentica correctamente
        messages.error(request, "Credenciales inválidas")

    return render(request, 'Landing/login.html')

def registro_cliente(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
            return redirect('login')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=correo,
            first_name=nombre
        )

        Cliente.objects.create(
            user=user,
            telefono=telefono
        )

        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect('login')

    return render(request, 'Landing/login.html')


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
    num_pagos = Pago.objects.count()

    context = {
        'num_barberos': num_barberos,
        'num_servicios': num_servicios,
        'num_citas': num_citas,
        'num_clientes': num_clientes,
        'num_pagos': num_pagos,
    }
    return render(request, 'cita/panel_control.html', context)

def nueva_cita(request):
    # Validar que el cliente esté autenticado
    if not request.user.is_authenticated:
        return redirect('login')  # o tu ruta de login

    try:
        # Obtener cliente vinculado al usuario logueado
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        return render(request, "cita/nueva_cita.html", {
            "error": "No estás registrado como cliente.",
            "servicios": Servicio.objects.all()
        })

    if request.method == "POST":
        fecha_hora = request.POST.get("fecha_hora")
        servicio_id = request.POST.get("servicio_id")
        estado = request.POST.get("estado", "Pendiente")

        try:
            servicio = Servicio.objects.get(id=servicio_id)
            fecha_hora = datetime.strptime(fecha_hora, "%Y-%m-%dT%H:%M")

            Cita.objects.create(
                cliente=cliente,
                fecha_hora=fecha_hora,
                servicio=servicio,
                estado=estado
            )
            return redirect("lista_citas")

        except Exception as e:
            return render(request, "cita/nueva_cita.html", {
                "error": str(e),
                "servicios": Servicio.objects.all()
            })

    context = {
        "servicios": Servicio.objects.all()
    }
    return render(request, "cita/nueva_cita.html", context)

def lista_citas(request):
    citas = Cita.objects.all()
    return render(request, 'cita/lista_citas.html', {'citas': citas})

def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    clientes = Cliente.objects.all()
    servicios = Servicio.objects.all()

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        fecha_hora = request.POST.get('fecha_hora')
        servicio_id = request.POST.get('servicio')
        estado = request.POST.get('estado')

        cita.cliente_id = cliente_id
        cita.fecha_hora = fecha_hora
        cita.servicio_id = servicio_id
        cita.estado = estado
        cita.save()

        return redirect('lista_citas')

    return render(request, 'cita/editar_cita.html', {
        'cita': cita,
        'clientes': clientes,
        'servicios': servicios
    })

# ✅ Función corregida
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    cita.delete()
    return redirect('lista_citas')

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

        return redirect('lista_servicios')

    return render(request, 'servicio/editar_servicio.html', {'servicio': servicio})

def eliminar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    servicio.delete()
    return redirect('lista_servicios')

def nuevo_horario(request):
    if request.method == "POST":
        barbero_id = request.POST.get("barbero_id")
        dias_seleccionados = request.POST.getlist("dias")  # Lista de días seleccionados

        try:
            if not barbero_id or not dias_seleccionados:
                raise Exception("Debe seleccionar un barbero y al menos un día.")

            barbero = Barbero.objects.get(id=barbero_id)

            for dia in dias_seleccionados:
                hora_inicio_str = request.POST.get(f"hora_inicio_{dia}")
                hora_fin_str = request.POST.get(f"hora_fin_{dia}")

                if not hora_inicio_str or not hora_fin_str:
                    raise Exception(f"Debe seleccionar hora de inicio y fin para {dia}.")

                hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
                hora_fin = datetime.strptime(hora_fin_str, "%H:%M").time()

                if hora_inicio >= hora_fin:
                    raise Exception(f"La hora de inicio para el día {dia} debe ser menor que la hora de fin.")

                # Validar superposición
                horarios_existentes = Horario.objects.filter(barbero=barbero, dia=dia)
                for horario in horarios_existentes:
                    if (hora_inicio < horario.hora_fin) and (hora_fin > horario.hora_inicio):
                        raise Exception(f"El horario para {dia} se solapa con otro ya asignado a {barbero.nombre}.")

                # Crear el nuevo horario
                Horario.objects.create(
                    barbero=barbero,
                    dia=dia,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )

            return redirect("lista_horarios")

        except Exception as e:
            return render(request, "horario/nuevo_horario.html", {
                "error": str(e),
                "barberos": Barbero.objects.all(),
                "dias": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            })

    return render(request, "horario/nuevo_horario.html", {
        "barberos": Barbero.objects.all(),
        "dias": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    })
    
def lista_horarios(request):
    horarios = Horario.objects.all()
    barberos_con_horarios = {}

    for horario in horarios:
        if horario.barbero not in barberos_con_horarios:
            barberos_con_horarios[horario.barbero] = []
        barberos_con_horarios[horario.barbero].append(horario)

    return render(request, 'horario/lista_horarios.html', {'barberos_con_horarios': barberos_con_horarios})

def eliminar_horario(request, horario_id):
    horario = get_object_or_404(Horario, id=horario_id)
    horario.delete()
    return redirect("lista_horarios")

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
            # Validar que el username no se repita (excepto el suyo)
            if User.objects.filter(username__iexact=username).exclude(id=user.id).exists():
                return render(request, 'admin_barbero/editar_barbero.html', {
                    'barbero': barbero,
                    'error': 'El nombre de usuario ya está en uso.'
                })

            try:
                # Actualizar datos del usuario
                user.first_name = nombre
                user.username = username
                user.email = email
                user.save()

                # Actualizar teléfono del barbero
                barbero.telefono = telefono
                barbero.save()

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

def landing(request):
    try:
        seccion = QuienesSomos.objects.get(id=1)  # Usa ID explícito
    except QuienesSomos.DoesNotExist:
        seccion = None

    return render(request, 'Landing/index.html', {'seccion': seccion})

def quienes_somos(request):
    seccion, created = QuienesSomos.objects.get_or_create(id=1)

    if request.method == 'POST':
        seccion.titulo = request.POST.get('titulo') 
        seccion.descripcion = request.POST.get('descripcion') 
        seccion.save()
        return redirect('index') 

    return render(request, 'paginas/quienes_somos.html', {'seccion': seccion})

def index_qs(request):
    contenido = QuienesSomos.objects.all()
    return render(request, 'Landing/index.html', {'contenido': contenido})

def ingresos_por_barbero(request):
    barberos = Barbero.objects.all()
    datos = []

    for barbero in barberos:
        pagos = Pago.objects.filter(
            cita__barbero=barbero,
            pagado=True
        )
        total = pagos.aggregate(Sum('monto'))['monto__sum'] or 0

        datos.append({
            'barbero': barbero.nombre,
            'total_ingresos': total,
        })

    return render(request, 'finanzas/ingresos_barbero.html', {'datos': datos})

def reporte_ingresos(request):
    total_ingresos = Pago.objects.filter(pagado=True).aggregate(Sum('monto'))['monto__sum'] or 0
    return render(request, 'finanzas/reporte_ingresos.html', {'total_ingresos': total_ingresos})

def ingresos_barbero(request):
    barberos = Barbero.objects.all()
    datos = []

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    for barbero in barberos:
        citas = Cita.objects.filter(barbero=barbero, estado='Completada')

        if fecha_inicio and fecha_fin:
            citas = citas.filter(fecha_hora__date__range=[fecha_inicio, fecha_fin])

        total = sum(cita.servicio.precio for cita in citas)
        comision = getattr(barbero.comision, 'porcentaje', 0)
        pago_barbero = total * (comision / 100)
        ingreso_barberia = total - pago_barbero

        datos.append({
            'barbero': barbero,
            'total': total,
            'comision': comision,
            'pago_barbero': pago_barbero,
            'ingreso_barberia': ingreso_barberia,
        })

    contexto = {
        'datos': datos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    return render(request, 'finanzas/ingresos_barbero.html', contexto)

def pagos(request):
    estado = request.GET.get('estado')  # 'realizado' o 'pendiente'
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    pagos = Pago.objects.all()

    if estado == 'realizado':
        pagos = pagos.filter(pagado=True)
    elif estado == 'pendiente':
        pagos = pagos.filter(pagado=False)

    if fecha_inicio:
        pagos = pagos.filter(fecha_pago__gte=fecha_inicio)
    if fecha_fin:
        pagos = pagos.filter(fecha_pago__lte=fecha_fin)

    return render(request, 'finanzas/pagos.html', {
        'pagos': pagos,
        'estado': estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })

def configurar_comisiones(request):
    barberos = Barbero.objects.all()
    return render(request, 'finanzas/configurar_comisiones.html', {'barberos': barberos})

def editar_comision(request, barbero_id):
    barbero = get_object_or_404(Barbero, id=barbero_id)
    comision, created = Comision.objects.get_or_create(barbero=barbero)

    if request.method == 'POST':
        porcentaje = request.POST.get('porcentaje')

        if porcentaje is None or porcentaje.strip() == "":
            # Mostrar un mensaje o manejar el error
            return render(request, 'finanzas/editar_comision.html', {
                'barbero': barbero,
                'comision': comision,
                'error': "El campo 'porcentaje' no puede estar vacío."
            })

        try:
            comision.porcentaje = float(porcentaje)
            comision.save()
            return redirect('configurar_comisiones')
        except ValueError:
            return render(request, 'finanzas/editar_comision.html', {
                'barbero': barbero,
                'comision': comision,
                'error': "Porcentaje inválido. Debe ser un número."
            })

    return render(request, 'finanzas/editar_comision.html', {
        'barbero': barbero,
        'comision': comision
    })


    #modelcliente
    
@login_required
def perfil_cliente(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
        citas = CitaCliente.objects.filter(
            cliente=cliente,
            visible_para_cliente=True  # 👈 solo las visibles
        ).select_related('servicio')
    except Cliente.DoesNotExist:
        cliente = None
        citas = []

    return render(request, 'cliente/perfil_cliente.html', {
        'cliente': cliente,
        'citas': citas,
    })

#AGENDAR CITA 

@login_required
def agendar_cita(request):
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        return render(request, "cliente/agendar_cita.html", {
            "error": "No estás registrado como cliente.",
            "barberos": Barbero.objects.filter(activo=True),
            "servicios": Servicio.objects.all(),
            "horarios_json": "{}"
        })

    if request.method == "POST":
        try:
            hora_str = request.POST.get("fecha_hora")  # Ej: "06:17"
            fecha_str = request.POST.get("fecha")       # También necesitamos la fecha
            servicio_id = request.POST.get("servicio")
            barbero_id = request.POST.get("barbero")
            estado = request.POST.get("estado", "pendiente")

            # Validaciones
            if not hora_str or not fecha_str or not servicio_id or not barbero_id:
                raise ValueError("Todos los campos obligatorios deben estar completos.")

            # Parseo
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            fecha_hora = datetime.combine(fecha_obj, hora_obj)

            servicio = Servicio.objects.get(id=servicio_id)
            barbero = get_object_or_404(Barbero, id=barbero_id, activo=True)

            # ✅ Validar si ya existe una cita para esa fecha y hora con ese barbero
            if CitaCliente.objects.filter(barbero=barbero, fecha_hora=fecha_hora).exists():
                raise ValueError("Esa hora ya está ocupada por otra cita. Por favor elige otra.")

            # Crear cita
            CitaCliente.objects.create(
                cliente=cliente,
                barbero=barbero,
                fecha_hora=fecha_hora,
                servicio=servicio,
                estado=estado
            )

            return redirect("perfil_cliente")

        except Exception as e:
            horarios_json = _generar_horarios_json()
            return render(request, "cliente/agendar_cita.html", {
                "error": str(e),
                "barberos": Barbero.objects.filter(activo=True),
                "servicios": Servicio.objects.all(),
                "horarios_json": horarios_json
            })

    # GET: Enviar horarios como JSON
    horarios_json = _generar_horarios_json()

    return render(request, "cliente/agendar_cita.html", {
        "barberos": Barbero.objects.filter(activo=True),
        "servicios": Servicio.objects.all(),
        "horarios_json": horarios_json
    })



def _generar_horarios_json():
    horarios_por_barbero = {}

    for horario in Horario.objects.all():
        barbero_id = str(horario.barbero.id)
        if barbero_id not in horarios_por_barbero:
            horarios_por_barbero[barbero_id] = []

        horario_str = f"{horario.dia} - {horario.hora_inicio.strftime('%H:%M')}"

        if horario_str not in horarios_por_barbero[barbero_id]:
            horarios_por_barbero[barbero_id].append(horario_str)

    return json.dumps(horarios_por_barbero, cls=DjangoJSONEncoder)


@login_required
def cambiar_estado_barbero(request):
    barbero = request.user.barbero
    if request.method == 'POST':
        barbero.activo = not barbero.activo
        barbero.save()
        return redirect('panel_barbero')
    return render(request, 'barbero/estado_barbero.html', {'barbero': barbero})



@login_required
def guardar_horario_disponible(request):
    if request.method == 'POST':
        fechas = request.POST.getlist('fecha[]')
        horas_inicio = request.POST.getlist('hora_inicio[]')
        horas_fin = request.POST.getlist('hora_fin[]')

        barbero = Barbero.objects.get(user=request.user)

        for f, h_ini, h_fin in zip(fechas, horas_inicio, horas_fin):
            HorarioDisponible.objects.create(
                barbero=barbero,
                fecha=f,
                hora_inicio=h_ini,
                hora_fin=h_fin
            )

        messages.success(request, "Horarios guardados correctamente.")
        return redirect('panel_barbero')
    
@login_required
def historial_citas_cliente(request):
    cliente = request.user.cliente  # Asumiendo que tu modelo Cliente tiene relación OneToOne con User
    citas = CitaCliente.objects.filter(cliente=cliente).order_by('-fecha_hora')
    return render(request, 'cliente/historial_citas.html', {
        'citas': citas
    })

@login_required
def eliminar_cita_cliente(request, cita_id):
    cliente = request.user.cliente
    cita = get_object_or_404(CitaCliente, id=cita_id, cliente=cliente)

    cita.visible_para_cliente = False
    cita.save()
    messages.success(request, "La cita fue eliminada de tu perfil.")
    return redirect('perfil_cliente')

@login_required
def eliminar_cita_barbero(request, cita_id):
    barbero = request.user.barbero
    cita = get_object_or_404(CitaCliente, id=cita_id, barbero=barbero)

    cita.visible_para_barbero = False
    cita.save()
    messages.success(request, "La cita fue eliminada del panel del barbero.")
    return redirect('citas_asignadas')


@login_required
def aceptar_cita(request, cita_id):
    print("✅ Aceptando cita", cita_id)
    cita = get_object_or_404(CitaCliente, id=cita_id, barbero=request.user.barbero)
    cita.estado = 'Aceptada'
    cita.save()
    return redirect('citas_asignadas_barbero')

@login_required
def rechazar_cita(request, cita_id):
    cita = get_object_or_404(CitaCliente, id=cita_id, barbero=request.user.barbero)
    cita.estado = 'Rechazada'
    cita.save()
    return redirect('citas_asignadas_barbero')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Barbero, CitaCliente

@login_required
def citas_asignadas_barbero(request):
    try:
        barbero = Barbero.objects.get(user=request.user)
    except Barbero.DoesNotExist:
        messages.error(request, "No sos barbero.")
        return redirect('home')

    citas = CitaCliente.objects.filter(
        barbero=barbero,
        visible_para_barbero=True  # 👈 solo las visibles para el barbero
    ).select_related('cliente', 'servicio').order_by('fecha_hora')

    return render(request, 'barbero/citas_asignadas.html', {
        'citas': citas,
        'barbero': barbero,
    })


@login_required
def finanzas_barbero(request):
    barbero = request.user.barbero
    hoy = date.today()
    citas_hoy = CitaCliente.objects.filter(
        barbero=barbero,
        estado='Aceptada',
        fecha_hora__date=hoy
    ).select_related('servicio', 'cliente')

    ingresos = sum([cita.servicio.precio for cita in citas_hoy])

    return render(request, 'barbero/finanzas.html', {
        'barbero': barbero,
        'citas_hoy': citas_hoy,
        'ingresos_dia': ingresos,
    })

@login_required
def guardar_horario_disponible(request):
    barbero = request.user.barbero
    if request.method == 'POST':
        dia_str = request.POST.get('dia')
        horas = request.POST.getlist('horas[]')

        if not dia_str or not horas:
            messages.error(request, "Debes seleccionar una fecha y al menos una hora.")
            return redirect('guardar_horario_disponible')

        fecha = datetime.strptime(dia_str, "%Y-%m-%d").date()

        for hora_str in horas:
            hora = datetime.strptime(hora_str, "%H:%M").time()
            HorarioDisponible.objects.create(
                barbero=barbero,
                fecha=fecha,
                hora=hora
            )

        messages.success(request, "Horarios guardados correctamente.")
        return redirect('panel_barbero')
    
    # Generar lista de horas: 8:00 AM a 8:00 PM en bloques de 30 mins
    horas = []
    inicio = time(8, 0)
    fin = time(20, 0)
    actual = datetime.combine(date.today(), inicio)
    while actual.time() <= fin:
        horas.append(actual.time().strftime("%H:%M"))
        actual += timedelta(minutes=30)

    return render(request, 'barbero/agregar_horario.html', {
        'horas': horas
    })


@login_required
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(CitaCliente, id=cita_id)

    user = request.user

    if hasattr(user, 'cliente') and cita.cliente.user == user:
        cita.delete()
        messages.success(request, "Tu cita ha sido eliminada con éxito.")
        return redirect('perfil_cliente')

    elif hasattr(user, 'barbero') and cita.barbero.user == user:
        cita.delete()
        messages.success(request, "Has eliminado la cita del cliente.")
        return redirect('citas_asignadas_barbero')

    else:
        messages.error(request, "No tienes permiso para eliminar esta cita.")
        return redirect('home')
    
@login_required
def panel_barbero(request):
    try:
        barbero = Barbero.objects.get(user=request.user)
    except Barbero.DoesNotExist:
        messages.error(request, "No sos barbero.")
        return redirect('home')

    hoy = date.today()

    citas = Cita.objects.filter(
        barbero=barbero
    ).select_related('cliente', 'servicio').order_by('fecha_hora')

    ingresos_hoy = Pago.objects.filter(
        cita__barbero=barbero,
        cita__fecha_hora__date=hoy,
        pagado=True
    ).aggregate(Sum('monto'))['monto__sum'] or 0

    horarios = HorarioDisponible.objects.filter(
        barbero=barbero,
        fecha__gte=hoy
    ).order_by('fecha', 'hora')  # 🛠️ CORREGIDO

    context = {
        'barbero': barbero,
        'citas': citas,
        'ingresos_hoy': ingresos_hoy,
        'horarios': horarios,
    }
    return render(request, 'barbero/panel_barbero.html', context)

@login_required
def obtener_horas_disponibles(request):
    barbero_id = request.GET.get('barbero_id')
    fecha_str = request.GET.get('fecha')

    if not barbero_id or not fecha_str:
        return JsonResponse({'error': 'Datos incompletos'}, status=400)

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

        # Obtener todos los horarios disponibles exactos para ese barbero y esa fecha
        horarios = HorarioDisponible.objects.filter(
            barbero_id=barbero_id,
            fecha=fecha
        )

        # Obtener todas las citas ya ocupadas
        horas_ocupadas = set(
            CitaCliente.objects.filter(
                barbero_id=barbero_id,
                fecha_hora__date=fecha
            ).values_list('fecha_hora', flat=True)
        )

        horas_ocupadas = set(hora.time() for hora in horas_ocupadas)

        # Armar la respuesta
        respuesta = []
        for horario in horarios:
            hora = horario.hora
            hora_str = hora.strftime("%H:%M")
            disponible = hora not in horas_ocupadas
            respuesta.append({
                "hora": hora_str,
                "disponible": disponible
            })

        return JsonResponse(respuesta, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

