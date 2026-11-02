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
		}, 200)

		respuesta = self.client.post('/login/', {
			'username': 'estudiante',
			'password': 'ClaveSegura123!',
		})

		self.assertRedirects(respuesta, '/', fetch_redirect_response=False)
		self.assertEqual(self.client.session['usuario'], 'estudiante')
		self.assertEqual(self.client.session['permisos'], ['view_reports'])
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

		self.assertContains(respuesta, 'href="#">Panel</a>')
		self.assertContains(respuesta, 'href="#">Reportes</a>')
		self.assertNotContains(respuesta, 'href="#">Usuarios</a>')
		self.assertNotContains(respuesta, 'href="#">Pagos</a>')
