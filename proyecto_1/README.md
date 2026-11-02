# Proyecto 1: API de permisos

## Ejecutar

```sh
cd proyecto_1
python -m pip install -r ../requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8050
```

La API guarda usuarios y permisos en `db.sqlite3`. El Proyecto 2 consume la API en `http://localhost:8050/api/`.

## Endpoints

- POST /api/autentificar/
- POST /api/agregarusuario/
- POST /api/actualizar/
- POST /api/addpermiso/
- POST /api/asociapermiso/

`autentificar` permite iniciar sesión y devuelve el usuario, sus permisos, servicios y un token. También se puede solicitar un token en `/api/token/`. Las operaciones de alta, cambio de contraseña y permisos requieren un usuario administrador y el encabezado `Authorization: Bearer <token>`.

## Pruebas

```sh
python manage.py test
```
