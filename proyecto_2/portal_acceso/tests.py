from unittest.mock import patch

from django.test import SimpleTestCase


class PortalAccesoTests(SimpleTestCase):
	@patch('portal_acceso.views._api_post')
	def test_login_valido_guarda_sesion_y_redirige_al_inicio(self, solicitud_api):
		solicitud_api.return_value = ({
			'ok': True,
			'user': {'username': 'estudiante'},
			'permisos': ['view_reports'],
			'servicios': {'reportes': True},
			'token': 'token-acceso',
		}, 200)

		respuesta = self.client.post('/login/', {
			'username': 'estudiante',
			'password': 'ClaveSegura123!',
		})

		self.assertRedirects(respuesta, '/', fetch_redirect_response=False)
		self.assertEqual(self.client.session['usuario'], 'estudiante')
		self.assertEqual(self.client.session['permisos'], ['view_reports'])
		self.assertNotIn('token', self.client.session)
		solicitud_api.assert_called_once_with('/autentificar/', {
			'username': 'estudiante',
			'password': 'ClaveSegura123!',
		})

	@patch('portal_acceso.views._api_post')
	def test_login_invalido_muestra_error(self, solicitud_api):
		solicitud_api.return_value = ({
			'ok': False,
			'detail': 'Credenciales inválidas.',
		}, 401)

		respuesta = self.client.post('/login/', {
			'username': 'estudiante',
			'password': 'incorrecta',
		})

		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'Credenciales inválidas.')
		self.assertNotIn('usuario', self.client.session)

	def test_inicio_redirige_si_no_hay_sesion(self):
		respuesta = self.client.get('/')

		self.assertRedirects(respuesta, '/login/', fetch_redirect_response=False)

	@patch('portal_acceso.views._api_post')
	def test_usuario_sin_permisos_ve_inicio_sin_secciones(self, solicitud_api):
		solicitud_api.return_value = ({
			'ok': True,
			'user': {'username': 'user'},
			'permisos': [],
			'servicios': {},
		}, 200)
		self.client.post('/login/', {'username': 'user', 'password': 'test1234'})

		respuesta = self.client.get('/')

		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'Sin opciones disponibles')
		self.assertNotContains(respuesta, 'Permisos del usuario')

	@patch('portal_acceso.views._api_post')
	def test_usuario_normal_no_abre_seccion_sin_servicio(self, solicitud_api):
		solicitud_api.return_value = ({
			'ok': True,
			'user': {'username': 'user'},
			'permisos': [],
			'servicios': {},
		}, 200)
		self.client.post('/login/', {'username': 'user', 'password': 'test1234'})

		self.assertEqual(self.client.get('/usuarios/').status_code, 403)
		solicitud_api.assert_called_once_with('/autentificar/', {
			'username': 'user',
			'password': 'test1234',
		})

	@patch('portal_acceso.views._api_post')
	def test_menu_muestra_solo_los_servicios_autorizados(self, solicitud_api):
		solicitud_api.return_value = ({
			'ok': True,
			'user': {'username': 'estudiante'},
			'permisos': ['view_reports'],
			'servicios': {
				'dashboard': True,
				'usuarios': False,
				'pagos': False,
				'reportes': True,
				'configuracion': False,
			},
		}, 200)
		self.client.post('/login/', {
			'username': 'estudiante',
			'password': 'ClaveSegura123!',
		})

		respuesta = self.client.get('/')

		self.assertContains(respuesta, 'href="/" aria-current="page">Panel</a>')
		self.assertContains(respuesta, 'href="/reportes/">Reportes</a>')
		self.assertNotContains(respuesta, 'href="/usuarios/">Usuarios</a>')
		self.assertNotContains(respuesta, 'href="/pagos/">Pagos</a>')
		self.assertNotContains(respuesta, 'Permisos del usuario')

	@patch('portal_acceso.views._api_post')
	def test_inicio_redirige_a_una_seccion_permitida_si_no_tiene_dashboard(self, solicitud_api):
		solicitud_api.return_value = ({
			'ok': True,
			'user': {'username': 'estudiante'},
			'permisos': ['view_reports'],
			'servicios': {'dashboard': False, 'reportes': True},
		}, 200)
		self.client.post('/login/', {'username': 'estudiante', 'password': 'clave'})

		respuesta = self.client.get('/')

		self.assertRedirects(respuesta, '/reportes/', fetch_redirect_response=False)

	@patch('portal_acceso.views._api_post')
	def test_secciones_abren_con_permisos_y_rechazan_acceso_directo_sin_permiso(self, solicitud_api):
		servicios = {
			'dashboard': True,
			'usuarios': True,
			'pagos': True,
			'reportes': True,
			'configuracion': True,
		}
		solicitud_api.return_value = ({
			'ok': True,
			'user': {'username': 'estudiante'},
			'permisos': [],
			'servicios': servicios,
		}, 200)
		self.client.post('/login/', {'username': 'estudiante', 'password': 'clave'})

		for ruta, titulo in (
			('/usuarios/', 'Usuarios'),
			('/pagos/', 'Pagos'),
			('/reportes/', 'Reportes'),
			('/configuracion/', 'Configuración'),
		):
			with self.subTest(ruta=ruta):
				respuesta = self.client.get(ruta)
				self.assertEqual(respuesta.status_code, 200)
				self.assertContains(respuesta, f'<h1>{titulo}</h1>')

		self.client.get('/logout/')
		servicios['usuarios'] = False
		solicitud_api.return_value = ({
			'ok': True,
			'user': {'username': 'estudiante'},
			'permisos': [],
			'servicios': servicios,
		}, 200)
		self.client.post('/login/', {'username': 'estudiante', 'password': 'clave'})
		self.assertEqual(self.client.get('/usuarios/').status_code, 403)

	def test_seccion_redirige_si_no_hay_sesion(self):
		respuesta = self.client.get('/reportes/')

		self.assertRedirects(respuesta, '/login/', fetch_redirect_response=False)
