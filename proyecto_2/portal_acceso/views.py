import json
from urllib import error, request

from django.contrib import messages
from django.shortcuts import redirect, render

API_URL = 'http://localhost:8050/api'


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
    if 'usuario' not in request.session:
        return redirect('iniciar_sesion')

    usuario = request.session.get('usuario')
    permisos = set(request.session.get('permisos', []))
    servicios = request.session.get('servicios', {})

    menu = {
        'Panel': servicios.get('dashboard', False),
        'Usuarios': servicios.get('usuarios', False),
        'Pagos': servicios.get('pagos', False),
        'Reportes': servicios.get('reportes', False),
        'Configuración': servicios.get('configuracion', False),
    }

    return render(request, 'portal_acceso/home.html', {
        'usuario': usuario,
        'menu': menu,
        'permisos': sorted(permisos),
    })


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
