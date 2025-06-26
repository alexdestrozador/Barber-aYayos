from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cita, Cliente, Servicio, Horario, Barbero, QuienesSomos, Pago, Comision
from datetime import datetime
from django.utils.timezone import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import PerfilAdminForm
from .models import AdminProfile
from django.utils.dateparse import parse_datetime
from datetime import timedelta

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
    if not request.user.is_superuser:
        return redirect('login')
    return render(request, 'Home/home.html')

def index(request):
    return render(request, 'Landing/index.html')

def home(request):
    return render(request, 'Home/home.html') # o 'home/home.html' según la estructura

def quienesomos(request):
    return render(request, 'paginas/quienesomos.html')

def contacto(request):
    return render(request, 'paginas/contacto.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Verificamos Barbero
        barbero = Barbero.objects.filter(username=username).first()
        if barbero and check_password(password, barbero.password):
            if not barbero.activo:
                messages.error(request, "Cuenta inactiva.")
                return redirect('login')
            request.session['usuario'] = barbero.username
            request.session['tipo'] = 'barbero'
            return redirect('panel_barbero')

        # Verificamos Cliente
        cliente = Cliente.objects.filter(username=username).first()
        if cliente and check_password(password, cliente.password):
            if not cliente.activo:
                messages.error(request, "Cuenta inactiva.")
                return redirect('login')
            request.session['usuario'] = cliente.username
            request.session['tipo'] = 'cliente'
            return redirect('panel_cliente')

        # Verificamos Admin por superusuario
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            login(request, user)  # Django maneja la sesión
            return redirect('panel_admin') 

        messages.error(request, "Credenciales inválidas")
    return render(request, 'Landing/login.html')

def registro_cliente(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')

        if Cliente.objects.filter(username=username).exists() or Barbero.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
            return redirect('login')

        Cliente.objects.create(
            username=username,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            password=make_password(password)  # ← aquí se encripta
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
        correo = request.POST.get('email', '').strip()  # 🔧 corrección aquí
        password_raw = request.POST.get('password', '').strip()

        if nombre and username and telefono and correo and password_raw:
            if Barbero.objects.filter(username__iexact=username).exists():
                return render(request, 'admin_barbero/nuevo_barbero.html', {
                    'error': 'El nombre de usuario ya está en uso.',
                    'form_data': request.POST
                })

            try:
                Barbero.objects.create(
                    nombre=nombre,
                    username=username,
                    telefono=telefono,
                    correo=correo,
                    password=make_password(password_raw)
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
        existe = Barbero.objects.filter(username__iexact=username).exclude(id=barbero_id).exists()
    else:
        existe = Barbero.objects.filter(username__iexact=username).exists()

    return JsonResponse({'existe': existe})

def lista_barberos(request):
    barberos = Barbero.objects.all()
    return render(request, 'admin_barbero/lista_barberos.html', {'barberos': barberos})

def editar_barbero(request, barbero_id):
    barbero = get_object_or_404(Barbero, id=barbero_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        username = request.POST.get('username', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()

        if nombre and username and telefono and email:
            # Validar que el username no se repita (excepto el suyo mismo)
            if Barbero.objects.filter(username__iexact=username).exclude(id=barbero.id).exists():
                error_msg = "El nombre de usuario ya está en uso. Elige otro."
                return render(request, 'admin_barbero/editar_barbero.html', {
                    'barbero': barbero,
                    'error': error_msg
                })

            try:
                barbero.nombre = nombre
                barbero.username = username
                barbero.telefono = telefono
                barbero.correo = email
                # No se toca barbero.password → se conserva
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