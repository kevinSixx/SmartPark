# Backend

API FastAPI de SmartPark (versión indicada por `/health`: 1.7.2), puerto 8000. Gestiona autenticación, usuarios, vehículos, permisos, garitas, perfiles faciales y eventos de acceso. Usa PostgreSQL/RDS para persistencia, llama a IA para procesar accesos, guarda medios en S3 y puede enviar comandos de barrera mediante AWS IoT Core.

## Estructura y dependencias

`app/main.py` es el punto de entrada; `app/routes/` define rutas, `app/services/` contiene servicios, `migrations/` es Alembic y `tests/` contiene pruebas. Las dependencias vigentes están en `requirements.txt`; no se cambiaron. `alembic.ini` y las migraciones permanecen intactos.

## Configuración

Ver `.env.example`. Se requiere `DATABASE_URL` y `AUTH_SECRET_KEY`; también se usan `AI_BASE_URL`, `AWS_REGION`, `SMARTPARK_MEDIA_BUCKET`, `AWS_IOT_ENABLED`, `AWS_IOT_ENDPOINT`, `AWS_IOT_COMMAND_TOPIC`, `BARRIER_OPEN_SECONDS` y `AUTH_TOKEN_MINUTES`. Definir valores privados solo en el entorno local. El ejemplo no conecta por sí solo a RDS/S3/IoT. No publicar credenciales ni ejecutar migraciones contra RDS para obtener evidencias.

## Inicio local

Desde `Proyecto/`, con dependencias ya presentes en `.venv` y PostgreSQL local configurado:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

`docker-compose.yml` de la raíz contiene `db` y `mqtt`; no levanta el Backend. Su Dockerfile usa **contexto `Proyecto/`**:

```powershell
docker build -f backend/Dockerfile -t smartpark-backend .
```

Esta línea documenta el contexto y no forma parte de las pruebas de esta organización. Para migraciones, revisar `alembic.ini` y usar `alembic upgrade head` solo sobre una base local autorizada.

## Comprobación y rutas

Con el servicio local iniciado: `GET /health`, `GET /db-check` y `/docs`. Las rutas de negocio están bajo `/api/v1/`, incluidas autenticación, acceso, usuarios, vehículos, permisos, personal, garitas y perfiles faciales. `GET /db-check` requiere una base disponible. Las pruebas existentes están en `backend/tests/`; antes de correrlas, confirmar que usan una base aislada.

## Errores frecuentes

`DATABASE_URL` o `AUTH_SECRET_KEY` ausentes impiden importar la aplicación. Un fallo de `/db-check` indica conexión/configuración de PostgreSQL. S3 e IoT requieren permisos y configuración reales; no probar comandos de barrera con recursos productivos.
