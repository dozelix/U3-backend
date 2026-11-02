import json
from urllib import error, request

from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render, reverse

API_URL = 'http://localhost:8050/api'
MENU_ITEMS = (
    ('Panel', 'dashboard', 'inicio'),
    ('Usuarios', 'usuarios', 'usuarios'),
    ('Pagos', 'pagos', 'pagos'),
    ('Reportes', 'reportes', 'reportes'),
    ('Configuración', 'configuracion', 'configuracion'),
)
SECCIONES = {
    'usuarios': 'Usuarios',
    'pagos': 'Pagos',
    'reportes': 'Reportes',
    'configuracion': 'Configuración',
}


def _api_post(endpoint, payload):
    data = json.dumps(payload).encode('utf-8')
    req = request.Request(
        f'{API_URL}{endpoint}',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')), response.status
    except error.HTTPError as exc:
        body = exc.read().decode('utf-8', 'ignore')
        try:
            return json.loads(body), exc.code
        except Exception:
            return {'ok': False, 'detail': body or 'Error de API'}, exc.code
    except Exception:
        return {'ok': False, 'detail': 'No se pudo conectar con la API.'}, 503


def inicio(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('iniciar_sesion')

    servicios = request.session.get('servicios', {})
    if not servicios.get('dashboard'):
        for _, service, route_name in MENU_ITEMS[1:]:
            if servicios.get(service):
                return redirect(route_name)
        return HttpResponseForbidden()

    return render(request, 'portal_acceso/home.html', {
        'usuario': usuario,
        'menu': _crear_menu(servicios, 'inicio'),
    })


def seccion(request, seccion):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('iniciar_sesion')

    if seccion not in SECCIONES:
        return HttpResponseForbidden()

    servicios = request.session.get('servicios', {})
    if not servicios.get(seccion):
        return HttpResponseForbidden()

    return render(request, 'portal_acceso/seccion.html', {
        'usuario': usuario,
        'menu': _crear_menu(servicios, seccion),
        'titulo': SECCIONES[seccion],
    })


def _crear_menu(servicios, ruta_activa):
    return [
        {
            'label': label,
            'url': reverse(route_name),
            'visible': servicios.get(service, False),
            'active': route_name == ruta_activa,
        }
        for label, service, route_name in MENU_ITEMS
    ]


def iniciar_sesion(request):
    if request.method == 'POST':
        payload = {
            'username': request.POST.get('username', ''),
            'password': request.POST.get('password', ''),
        }
        response, status_code = _api_post('/autentificar/', payload)

        if status_code == 200 and response.get('ok'):
            request.session['usuario'] = response['user']['username']
            request.session['permisos'] = response.get('permisos', [])
            request.session['servicios'] = response.get('servicios', {})
            request.session.modified = True
            return redirect('inicio')

        messages.error(request, response.get('detail', 'Credenciales inválidas.'))
        return render(request, 'portal_acceso/login.html')

    return render(request, 'portal_acceso/login.html')


def cerrar_sesion(request):
    request.session.flush()
    return redirect('iniciar_sesion')
