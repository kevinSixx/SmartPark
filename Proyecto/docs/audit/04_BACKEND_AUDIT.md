# 04. Auditoría Backend

`backend/app/main.py` crea FastAPI 1.7.2 y monta ocho routers. Docker inicia `uvicorn backend.app.main:app` en 8000; requiere contexto de build en raíz por `COPY backend/...`. `database.py` exige `DATABASE_URL` al importarse. SQLAlchemy 2.0 define `users`, `vehicles`, `permissions`, `access_events`, `face_profiles`, `face_samples`, `staff_accounts`, `gate_actions`. Los esquemas Pydantic están en `app/schemas/`; lógica de negocio en `app/services/`; Alembic en `backend/migrations/`.

| Dominio | Ruta/servicio | Operación y dependencia |
|---|---|---|
| Usuarios y vehículos | `routes/users.py`, `routes/vehicles.py`; services homónimos | CRUD parcial y relación usuario–vehículo; DB |
| Permisos y eventos | `routes/permissions.py`, `routes/access_events.py` | Vigencia, historial, `POST /api/v1/access/process` reenvía multipart a `AI_BASE_URL/process` |
| Autorización | `routes/access_events.py:340`, `services/authorization.py` | AI llama `/access/authorize`; registra decisión; acción automática IoT en background cuando autorizado |
| Caras | `routes/face_profiles.py`, `services/face_profiles.py` | Enrolamiento de 3–5 fotos → AI `/face/enroll`, guarda embeddings en RDS y fotos en S3; `/match` compara coseno con umbral `FACE_MATCH_THRESHOLD` |
| JWT y personal | `routes/auth.py`, `routes/staff.py`, `services/auth.py`, `services/staff_accounts.py` | PBKDF2-HMAC para contraseñas, JWT HS256; ADMIN gestiona personal, ADMIN/GUARD controlan barrera |
| Barrera | `routes/gates.py`, `services/gate_actions.py`, `mqtt/client.py` | Abre/cierra vía boto3 IoT Data Plane y audita acciones; requiere IAM y topic |
| Salud | `main.py:177,198` | `/health` no consulta DB; `/db-check` ejecuta `SELECT 1` |

## Seguridad y red

`AUTH_SECRET_KEY` es obligatorio (`services/auth.py:40-58`). Solo `/auth/me`, `staff` y `gates` muestran dependencias JWT en rutas. Usuarios, vehículos, permisos, eventos, proceso, autorización y perfiles faciales **no tienen protección JWT visible en sus firmas**; en particular `/access/authorize` y `/face-profiles/match` son interfaces internas expuestas si el ALB/API Gateway no las restringe. Confirmar reglas de API Gateway/ALB y decidir control servidor antes de entrega pública. CORS en `main.py:73-88` permite Vite localhost:5173/5174, un sitio S3 antiguo y Amplify production. S3 usa `SMARTPARK_MEDIA_BUCKET`, IAM y `boto3`; IoT usa `AWS_IOT_ENDPOINT`, `AWS_IOT_COMMAND_TOPIC`, `AWS_IOT_ENABLED`.

## Migraciones, pruebas y puntos dudosos

Seis archivos Alembic forman cadena desde `dda2992a9d8b` hasta `7f2c9d1a4b6e`; hay **dos revisiones con nombre «add_face_profiles_and_samples»** (`0945...` y `8e1...`) pero IDs y dependencias distintos. No son duplicados demostrados: revisar SQL/DDL y estado de base antes de tocar. `backend/tests/test_api.py` y `conftest.py` existen; no se ejecutaron pruebas por poder crear estado en base y caché. `app/scripts/create_admin.py` y `create_guard_tables.py` son comandos administrativos, no entrypoints automáticos. `models/__init__.py` importa algunos modelos, mientras las migraciones más recientes incorporan `staff_account` y `gate_action`; comprobar metadata Alembic y autogenerate en entorno aislado.

## Código muerto/imports

No se concluye que un módulo esté muerto por ausencia de import: rutas, scripts, migraciones, tests y llamadas HTTP cuentan como usos. Un barrido AST de imports no utilizados señaló `AccessEvent` en `create_guard_tables.py`, pero el comentario del propio script indica un import por efecto de registro de modelos; **no se clasifica como eliminable**. Candidatos para revisión manual: `create_guard_tables.py` frente a migración de personal/barrera y scripts de admin frente a provisión por API. En esta etapa no se aplicó linter ejecutable ni se eliminó código.

Lista exhaustiva de métodos/rutas y contratos: [13_ENDPOINTS.md](13_ENDPOINTS.md).
