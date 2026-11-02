# Proyecto 2: Portal de acceso

## Ejecutar

```powershell
cd proyecto_2
python manage.py runserver 0.0.0.0:8000
```

## Integración

Inicia primero el Proyecto 1 con `runserver` en el puerto `8050`. El login consume `http://localhost:8050/api/autentificar/`.

El portal solo consulta `autentificar` y configura el menú con los servicios recibidos. La sección Usuarios no crea cuentas desde el Proyecto 2; el endpoint de alta está disponible en la UI de la API del Proyecto 1.

## Restricciones

- Sin formularios automáticos.
- Sin admin de Django.
- Sin base de datos local.

## Pruebas

```sh
python manage.py test
```
