# Proyecto API de permisos

## Ejecutar

```powershell
cd "t:\U3 backend\api_service"
..\..\.venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8050
```

## Endpoints

- POST /api/autentificar/
- POST /api/agregarusuario/
- POST /api/actualizar/
- POST /api/addpermiso/
- POST /api/asociapermiso/

## Ejemplo de autenticación

```json
{
  "username": "admin",
  "password": "123456"
}
```
