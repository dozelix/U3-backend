# Evaluación Práctica 03

La entrega contiene exactamente los dos proyectos solicitados:

- [Proyecto 1: API de permisos](proyecto_1/README.md), Django REST Framework y SQLite en el puerto `8050`.
- [Proyecto 2: Portal de acceso](proyecto_2/README.md), login y menú según permisos en el puerto `8000`, sin base de datos.

## Preparación

Desde la raíz del repositorio:

```sh
python -m pip install -r requirements.txt
```

Inicia cada proyecto en una terminal separada. Primero prepara y ejecuta la API:

```powershell
cd proyecto_1
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; user, _ = User.objects.get_or_create(username='user'); user.is_staff = False; user.is_superuser = False; user.set_password('test1234'); user.save()"
python manage.py runserver 0.0.0.0:8050
```

La interfaz navegable propia de la API queda en `http://localhost:8050/api/` y su login en `http://localhost:8050/api-auth/login/`; no depende del portal del puerto `8000`.

Luego ejecuta el portal:

```sh
cd proyecto_2
python manage.py runserver 0.0.0.0:8000
```

## Pruebas locales

Ejecuta cada suite desde su carpeta:

```sh
cd proyecto_1 && python manage.py test
cd ../proyecto_2 && python manage.py test
```

## Dev Container

En VS Code, ejecuta **Reopen in Container**. La creación del contenedor instala las dependencias, prepara las migraciones de la API y ejecuta los checks y tests de ambos proyectos. Los puertos `8000` y `8050` quedan reenviados automáticamente.
