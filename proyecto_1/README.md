# Proyecto 1: API de permisos

## Ejecutar

```powershell
cd proyecto_1
python -m pip install -r ../requirements.txt
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; user, _ = User.objects.get_or_create(username='user'); user.is_staff = False; user.is_superuser = False; user.set_password('test1234'); user.save()"
python manage.py runserver 0.0.0.0:8050
```

La API guarda usuarios y permisos en `db.sqlite3`. Su interfaz navegable está en `http://localhost:8050/api/`; inicia sesión para operaciones protegidas en `http://localhost:8050/api-auth/login/`. Los formularios de navegador usan autenticación de sesión y los clientes externos pueden seguir usando JWT. El Proyecto 2 consume la API en `http://localhost:8050/api/`.

## Endpoints

- POST /api/autentificar/
- POST /api/agregarusuario/
- POST /api/actualizar/
- POST /api/addpermiso/
- POST /api/asociapermiso/

`autentificar` permite iniciar sesión y devuelve el usuario, sus permisos, servicios y un token. También se puede solicitar un token en `/api/token/`. Las operaciones de alta, cambio de contraseña y permisos requieren `is_staff=True` y el encabezado `Authorization: Bearer <token>`. La cuenta `user` se configura como usuario normal; estas operaciones permanecen protegidas y pueden responder 403 para esa cuenta.

## Pruebas

```sh
python manage.py test
```
