# Proyecto 2: Portal de acceso

## Ejecutar

```sh
cd proyecto_2
python manage.py runserver 0.0.0.0:8000
```

## Integración

El formulario de inicio de sesión consume `http://localhost:8050/api/autentificar/`. Inicia primero el Proyecto 1.

## Restricciones

- Sin formularios automáticos.
- Sin admin de Django.
- Sin base de datos local.

## Pruebas

```sh
python manage.py test
```
