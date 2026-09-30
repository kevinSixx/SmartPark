# SmartPark UCE

Sistema académico de control de acceso vehicular con ESP32, cámara Edge, servicios FastAPI y una interfaz React. **La raíz funcional es esta carpeta `Proyecto/`**. El entorno existente está en `.venv/`; esta organización conserva los originales operativos y agrega copias ordenadas para validar antes de preparar GitHub/ZIP.

## Arquitectura y flujo

1. El ESP32 mide distancia con HC-SR04 y publica `VEHICLE_DETECTED` por MQTT/mTLS en AWS IoT Core; recibe `OPEN`/`CLOSE` para el SG90.
2. Edge consume el evento, procesa cámara/DroidCam con YOLO11n y ByteTrack, determina ENTRY/EXIT, selecciona imágenes de rostro y matrícula mediante YuNet y YOLOv8n, y envía el caso al Backend.
3. Backend FastAPI valida autorización, coordina IA y persiste datos en PostgreSQL/RDS; puede usar S3 e IoT Core.
4. IA FastAPI usa RetinaFace, ArcFace/DeepFace y OCR. OCR FastAPI usa PaddleOCR en CPU.
5. Frontend React/Vite consume Backend y el estado/vídeo local del Edge. En cloud, Frontend fue desplegado en Amplify.

## Estructura

| Ruta | Función |
| --- | --- |
| `backend/` | API :8000, Alembic, Dockerfile y pruebas |
| `ai/` | servicio IA :8001 y seguimiento |
| `ocr/` | servicio OCR :8002 |
| `frontend/` | aplicación Vite de Amplify |
| `edge/` | **copia** organizada de Edge :9000, modelos e instalador fuente |
| `firmware/esp32/` | **copia** del sketch físico |
| `infra/` | descripción de Docker local y AWS |
| `docs/` | auditoría, organización, pruebas y evidencias |
| `.venv/` | entorno Python original local, excluido de entrega |

Las fuentes Edge, el firmware y los modelos están organizados en `edge/`, `firmware/esp32/` y `models/`. También existe `smartpark_edge_installer/` con fuentes y artefactos locales; conservar sus fuentes en la entrega. El peso YOLO11n usado por el build de IA está en `edge/models/yolo11n.pt`; el Dockerfile lo copia desde allí sin depender de una copia local en la raíz. Ver [modelos](models/README.md) e [informe de organización](docs/reorganization/IN_PLACE_ORGANIZATION.md).

## Requisitos y hardware

Usar el Python del entorno **ya existente** `Proyecto/.venv/Scripts/python.exe` en Windows. Frontend requiere Node y sus `node_modules` ya presentes para las comprobaciones sin instalar. La integración física requiere ESP32, HC-SR04, SG90, cámara compatible o DroidCam, red y certificados IoT privados. Backend necesita PostgreSQL; las integraciones AWS exigen recursos y permisos propios. Cada módulo documenta sus dependencias vigentes sin cambiar versiones.

## Modelos

Edge usa YOLO11n, ByteTrack (`bytetrack_smartpark.yaml`), YuNet y YOLOv8n para matrícula. IA usa RetinaFace, ArcFace y DeepFace; OCR usa PaddleOCR. Los tres archivos de modelo copiados a `edge/models/` tienen hashes registrados en el informe. No se descargó ni convirtió ningún modelo. Revisar licencia de cada modelo antes de publicarlo.

## Configuración e inicio local

Leer los `.env.example` de `backend/`, `ai/`, `ocr/`, `frontend/` y `edge/smartpark_edge_config.example.json`. Los ejemplos no son credenciales. Evitar el arranque con valores que apunten a AWS productivo. Desde `Proyecto/` y solo cuando exista un entorno local aislado:

```powershell
.\.venv\Scripts\python.exe -m uvicorn ocr.main:app --host 127.0.0.1 --port 8002
.\.venv\Scripts\python.exe -m uvicorn ai.main:app --host 127.0.0.1 --port 8001
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Cada servicio necesita su propia terminal y configuración. Para Frontend, desde `frontend/` ejecutar `npm run dev` con dependencias ya presentes. Para Edge, revisar primero [su README](edge/README.md), configurar cámara/certificados locales y entonces usar `.\.venv\Scripts\python.exe edge\smartpark_edge_production.py`. El firmware se compila/carga desde Arduino IDE siguiendo [su README](firmware/esp32/README.md). **No se iniciaron esos servicios durante esta organización.**

## Docker y AWS

El `docker-compose.yml` original en la raíz solo define PostgreSQL y Mosquitto para desarrollo. Los Dockerfiles de Backend, IA y OCR siguen en cada carpeta; sus contextos están indicados en sus README. Docker local no replica AWS. El despliegue AWS documentado comprende Amplify, API Gateway, ALB/ASG de Backend, ALB interno/ASG de IA, RDS, S3, ECR e IoT Core. Ninguno de esos recursos fue modificado. Ver [infraestructura](infra/README.md) y [auditoría](docs/audit/).

## Endpoints y pruebas

Backend: `/health`, `/db-check` y rutas `/api/v1/`; IA: `/health`, `/ready`, `/process`, `/face`, `/face/enroll`; OCR: `/health`, `/plate`; Edge: `/health`, `/status`, `/video`. Los puertos son 8000, 8001, 8002 y 9000 respectivamente. Consultar OpenAPI de cada servicio cuando se inicien en un entorno de prueba. En esta fase solo se permiten comprobaciones de sintaxis, imports disponibles y SHA-256; el informe registra el resultado y las pruebas de servicios pendientes.

## Seguridad, evidencias y entrega

`.gitignore` excluye `.venv`, `node_modules`, compilados, archivos `.env`, secretos, certificados privados, datos biométricos y ZIP/EXE. **Ignorar no retira archivos ya versionados ni limpia el historial Git**: revisar el índice, rotar cualquier credencial antes publicada y sanear el historial antes de GitHub público. Conservar pruebas y capturas reales en `docs/evidence/`; no publicar datos personales. Antes de generar ZIP/GitHub, verificar licencias de modelos, elegir una única copia Edge después de probarla, excluir backups/artefactos y revisar secretos. La lista de pendientes está en `docs/reorganization/IN_PLACE_ORGANIZATION.md`.
