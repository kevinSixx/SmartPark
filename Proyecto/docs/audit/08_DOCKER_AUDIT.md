# 08. Auditoría Docker

| Archivo | Contexto necesario según `COPY` | Base/puerto | Arranque | Observación |
|---|---|---|---|---|
| `.dockerignore` | Raíz `Proyecto/` | — | — | Excluye venv, Node, builds y scripts Edge, pero revisar alcance antes de cualquier build |
| `backend/Dockerfile` | Raíz `Proyecto/` (`COPY backend/...`) | `python:3.11-slim`, 8000 | `uvicorn backend.app.main:app` | No contiene migración automática |
| `ai/Dockerfile` | Raíz `Proyecto/` (`COPY edge/models/yolo11n.pt`, `COPY ai/...`) | `python:3.11-slim`, 8001 | `uvicorn ai.main:app` | Precarga DeepFace/ArcFace/RetinaFace durante build; salud por `/health` |
| `ocr/Dockerfile` | Carpeta `Proyecto/ocr/` (`COPY requirements.txt`, `COPY . /app/ocr`) | `paddlepaddle/paddle:2.6.2`, 8002 | `uvicorn ocr.main:app` | Si se usa contexto raíz copiaría archivos equivocados; verificar caché/modelos Paddle |
| `docker-compose.yml` | Raíz `Proyecto/` | DB 5432, Mosquitto 1883 | `db`, `mqtt` | No define Backend, IA ni OCR |

El Compose usa volumen `smartpark_postgres_data`, credencial local de desarrollo embebida y mount `./mosquitto/mosquitto.conf`; la carpeta ahora tiene la misma capitalización. La corrección de ruta no cambia la configuración MQTT. Tampoco hay una red explícita para resolver `smartpark_ocr`; Compose crea una red por proyecto, pero el servicio tendría que existir con ese nombre/alias. Las configuraciones cloud por defecto de IA apuntan a ALB Backend; para un Compose local hay que inyectar URLs internas.

## Propuesta de Compose LOCAL (sin aplicarla)

Servicios `backend`, `ai`, `smartpark_ocr` y `db` opcional, con builds `backend`/`ai` desde `context: .` y OCR desde `context: ./ocr`; red privada común y healthchecks separados. Backend usaría `DATABASE_URL` hacia `db:5432` y `AI_BASE_URL=http://ai:8001`; IA usaría `OCR_SERVICE_URL=http://smartpark_ocr:8002/plate`, `BACKEND_AUTHORIZE_URL=http://backend:8000/api/v1/access/authorize` y `BACKEND_FACE_MATCH_URL=http://backend:8000/api/v1/face-profiles/match`. Publicar 8000 para pruebas, 8001/8002 solo si se prueban individualmente. Secretos mediante `.env` local no versionado o secret store, nunca literales en YAML. PostgreSQL opcional mediante perfil; migraciones como comando explícito y respaldable. Edge Windows/cámara queda fuera de Docker local si el acceso a DroidCam/GUI es necesario. AWS IoT Core, RDS, S3, ALB, API Gateway y Amplify son servicios externos y no deben simularse en el Compose como si fueran equivalentes. Mosquitto local solo sirve para pruebas MQTT con payload/topic compatibles, no reemplaza mTLS/IAM de IoT Core.

No se encontraron tags ECR definitivos en Dockerfiles. Para publicación, fijar digest de bases, versión de paquetes y procedencia de pesos; verificar tags de imágenes desde el registro AWS con evidencia externa.
