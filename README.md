# Payment Platform Template

Proyecto Django con una app de frontend y una app de API REST para una plataforma de pagos.

## Requisitos

- Python 3.13
- Entorno virtual en `.venv`

## Activar entorno

```powershell
cd "t:\U3 backend"
.\.venv\Scripts\Activate.ps1
```

## Ejecutar frontend

```powershell
python manage.py runserver 0.0.0.0:8000 --settings=payment_platform.frontend_settings
```

## Ejecutar API REST

```powershell
python manage.py runserver 0.0.0.0:8080 --settings=payment_platform.api_settings
```

## Base de datos

Se usa SQLite por defecto:

```text
T:\U3 backend\db.sqlite3
```

## Endpoints de la API

- `http://localhost:8080/api/health/`
- `http://localhost:8080/api/payments/`

## Frontend

- `http://localhost:8000/`
