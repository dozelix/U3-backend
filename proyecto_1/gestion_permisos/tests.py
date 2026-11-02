from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase


class PermisosApiTests(APITestCase):
	def setUp(self):
		self.usuario = User.objects.create_user(
			username='estudiante',
			password='ClaveSegura123!',
		)
		self.operador = User.objects.create_user(
			username='operador_prueba',
			password='ClaveSegura123!',
			is_staff=True,
		)

	def autenticar_como(self, usuario, password='ClaveSegura123!'):
		respuesta = self.client.post('/api/token/', {
			'username': usuario.username,
			'password': password,
		}, format='json')
		self.assertEqual(respuesta.status_code, 200)
		self.client.credentials(
			HTTP_AUTHORIZATION=f"Bearer {respuesta.data['access']}"
		)

	def test_autentificar_retorna_usuario_y_servicios(self):
		respuesta = self.client.post('/api/autentificar/', {
			'username': 'estudiante',
			'password': 'ClaveSegura123!',
		}, format='json')

		self.assertEqual(respuesta.status_code, 200)
		self.assertTrue(respuesta.data['ok'])
		self.assertIn('servicios', respuesta.data)
		self.assertIn('token', respuesta.data)

	def test_api_tiene_indice_navegable_y_login_de_sesion(self):
		inicio = self.client.get('/', HTTP_HOST='localhost')
		respuesta = self.client.get('/api/', HTTP_HOST='localhost', HTTP_ACCEPT='text/html')
		login = self.client.get('/api-auth/login/', HTTP_HOST='localhost')

		self.assertRedirects(inicio, '/api/', fetch_redirect_response=False)
		self.assertEqual(respuesta.status_code, 200)
		self.assertContains(respuesta, 'autentificar')
		self.assertContains(respuesta, 'agregarusuario')
		self.assertEqual(login.status_code, 200)

	def test_interfaz_navegable_muestra_campos_de_autenticacion(self):
		respuesta = self.client.get(
			'/api/autentificar/',
			HTTP_HOST='localhost',
			HTTP_ACCEPT='text/html',
		)

		self.assertEqual(respuesta.status_code, 405)
		self.assertContains(respuesta, 'name="username"', status_code=405)
		self.assertContains(respuesta, 'name="password"', status_code=405)
		self.assertContains(respuesta, 'type="password"', status_code=405)

	def test_interfaz_navegable_muestra_campos_de_gestion(self):
		self.assertTrue(self.client.login(
			username=self.operador.username,
			password='ClaveSegura123!',
		))
		endpoints = (
			('/api/agregarusuario/', ('username', 'password', 'email')),
			('/api/actualizar/', ('username', 'new_password')),
			('/api/addpermiso/', ('nombre', 'codename')),
			('/api/asociapermiso/', ('username', 'permiso', 'nombre', 'codename')),
		)

		for endpoint, campos in endpoints:
			with self.subTest(endpoint=endpoint):
				respuesta = self.client.get(
					endpoint,
					HTTP_HOST='localhost',
					HTTP_ACCEPT='text/html',
				)
				self.assertEqual(respuesta.status_code, 405)
				for campo in campos:
					self.assertContains(respuesta, f'name="{campo}"', status_code=405)

	def test_operador_temporal_puede_operar_desde_la_interfaz_navegable(self):
		self.assertTrue(self.client.login(
			username=self.operador.username,
			password='ClaveSegura123!',
		))
		respuesta = self.client.post(
			'/api/addpermiso/',
			{'nombre': 'permiso_desde_ui'},
			HTTP_HOST='localhost',
			HTTP_ACCEPT='text/html',
			format='multipart',
		)

		self.assertEqual(respuesta.status_code, 201)
		self.assertIn('text/html', respuesta['Content-Type'])
		self.assertTrue(Permission.objects.filter(codename='permiso_desde_ui').exists())

	def test_autentificar_rechaza_credenciales_invalidas(self):
		respuesta = self.client.post('/api/autentificar/', {
			'username': 'estudiante',
			'password': 'incorrecta',
		}, format='json')

		self.assertEqual(respuesta.status_code, 401)

	def test_usuario_recibe_solo_los_servicios_de_sus_permisos(self):
		permiso = Permission.objects.create(
			name='Ver informes',
			codename='ver_informes',
			content_type=ContentType.objects.get_for_model(User),
		)
		self.usuario.user_permissions.add(permiso)
		respuesta = self.client.post('/api/autentificar/', {
			'username': self.usuario.username,
			'password': 'ClaveSegura123!',
		}, format='json')

		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual(respuesta.data['permisos'], ['ver_informes'])
		self.assertEqual(respuesta.data['servicios'], {
			'dashboard': False,
			'usuarios': False,
			'pagos': False,
			'reportes': True,
			'configuracion': False,
		})

	def test_rol_staff_no_activa_servicios_sin_permiso_asociado(self):
		respuesta = self.client.post('/api/autentificar/', {
			'username': self.operador.username,
			'password': 'ClaveSegura123!',
		}, format='json')

		self.assertEqual(respuesta.status_code, 200)
		self.assertFalse(respuesta.data['servicios']['usuarios'])
		self.assertFalse(respuesta.data['servicios']['dashboard'])

	def test_no_publica_interfaz_admin(self):
		self.assertEqual(self.client.get('/admin/').status_code, 404)

	def test_endpoints_de_gestion_requieren_administrador(self):
		endpoints = (
			('/api/agregarusuario/', {'username': 'nuevo', 'password': 'ClaveSegura123!'}),
			('/api/actualizar/', {'username': 'estudiante', 'new_password': 'OtraClave123!'}),
			('/api/addpermiso/', {'nombre': 'view_reportes'}),
			('/api/asociapermiso/', {'username': 'estudiante', 'permiso': 'view_reportes'}),
		)

		for endpoint, datos in endpoints:
			with self.subTest(endpoint=endpoint):
				self.assertEqual(self.client.post(endpoint, datos, format='json').status_code, 403)

				self.autenticar_como(self.usuario)
				self.assertEqual(self.client.post(endpoint, datos, format='json').status_code, 403)
				self.client.credentials()

	def test_operador_temporal_crea_usuario_y_actualiza_clave(self):
		self.autenticar_como(self.operador)

		respuesta_alta = self.client.post('/api/agregarusuario/', {
			'username': 'nuevo',
			'password': 'ClaveSegura123!',
		}, format='json')
		respuesta_clave = self.client.post('/api/actualizar/', {
			'username': 'estudiante',
			'new_password': 'OtraClave123!',
		}, format='json')

		self.assertEqual(respuesta_alta.status_code, 201)
		self.assertEqual(respuesta_clave.status_code, 200)
		self.usuario.refresh_from_db()
		self.assertTrue(self.usuario.check_password('OtraClave123!'))

	def test_endpoints_rechazan_contrasenas_debiles(self):
		self.autenticar_como(self.operador)
		respuesta_alta = self.client.post('/api/agregarusuario/', {
			'username': 'clave_debil',
			'password': '123',
		}, format='json')
		respuesta_cambio = self.client.post('/api/actualizar/', {
			'username': self.usuario.username,
			'new_password': '123',
		}, format='json')

		self.assertEqual(respuesta_alta.status_code, 400)
		self.assertEqual(respuesta_cambio.status_code, 400)
		self.assertFalse(User.objects.filter(username='clave_debil').exists())
		self.usuario.refresh_from_db()
		self.assertTrue(self.usuario.check_password('ClaveSegura123!'))

	def test_operador_temporal_crea_y_asocia_permiso(self):
		self.autenticar_como(self.operador)
		respuesta_permiso = self.client.post('/api/addpermiso/', {
			'nombre': 'ver_informes',
		}, format='json')
		respuesta_asociacion = self.client.post('/api/asociapermiso/', {
			'username': self.usuario.username,
			'permiso': 'ver_informes',
		}, format='json')

		self.assertEqual(respuesta_permiso.status_code, 201)
		self.assertEqual(respuesta_asociacion.status_code, 200)
		self.assertIn('ver_informes', respuesta_asociacion.data['permisos_actuales'])
