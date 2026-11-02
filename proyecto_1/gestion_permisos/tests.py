from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class PermisosApiTests(APITestCase):
	def setUp(self):
		self.usuario = User.objects.create_user(
			username='estudiante',
			password='ClaveSegura123!',
		)
		self.administrador = User.objects.create_user(
			username='administrador',
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

	def test_autentificar_rechaza_credenciales_invalidas(self):
		respuesta = self.client.post('/api/autentificar/', {
			'username': 'estudiante',
			'password': 'incorrecta',
		}, format='json')

		self.assertEqual(respuesta.status_code, 401)

	def test_endpoints_de_gestion_requieren_administrador(self):
		endpoints = (
			('/api/agregarusuario/', {'username': 'nuevo', 'password': 'ClaveSegura123!'}),
			('/api/actualizar/', {'username': 'estudiante', 'new_password': 'OtraClave123!'}),
			('/api/addpermiso/', {'nombre': 'view_reportes'}),
			('/api/asociapermiso/', {'username': 'estudiante', 'permiso': 'view_reportes'}),
		)

		for endpoint, datos in endpoints:
			with self.subTest(endpoint=endpoint):
				self.assertEqual(self.client.post(endpoint, datos, format='json').status_code, 401)

				self.autenticar_como(self.usuario)
				self.assertEqual(self.client.post(endpoint, datos, format='json').status_code, 403)
				self.client.credentials()

	def test_administrador_crea_usuario_y_actualiza_clave(self):
		self.autenticar_como(self.administrador)

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

	def test_administrador_crea_y_asocia_permiso(self):
		self.autenticar_como(self.administrador)
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
