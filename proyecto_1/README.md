# Proyecto 1: API de permisos

## Ejecutar

```sh
cd proyecto_1
python -m pip install -r ../requirements.txt
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user(username='staffuser', password='test1234', is_staff=True); User.objects.create_user(username='user', password='test1234')"
python manage.py runserver 0.0.0.0:8050
```

La API guarda usuarios y permisos en `db.sqlite3`. El Proyecto 2 consume la API en `http://localhost:8050/api/`.

## Endpoints

- POST /api/autentificar/
- POST /api/agregarusuario/
- POST /api/actualizar/
- POST /api/addpermiso/
- POST /api/asociapermiso/

`autentificar` permite iniciar sesión y devuelve el usuario, sus permisos, servicios y un token. También se puede solicitar un token en `/api/token/`. Las operaciones de alta, cambio de contraseña y permisos requieren `is_staff=True` y el encabezado `Authorization: Bearer <token>`. `staffuser` es un operador staff sin privilegios de superusuario; la interfaz Django Admin no está habilitada.

## Pruebas

```sh
python manage.py test
```
