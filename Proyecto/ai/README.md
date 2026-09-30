# IA

Servicio FastAPI de visión y biometría en el puerto 8001 (`ai/main.py`, versión 2.8.1). Combina detección y seguimiento de vehículo, RetinaFace para detectar rostros, ArcFace mediante DeepFace para representaciones faciales y comunicación con OCR y Backend. La inicialización de modelos realiza warmup y algunas operaciones se ejecutan en un threadpool. Las decisiones y umbrales siguen en el código original.

## Configuración y dependencias

Conservar `requirements.txt` y los modelos existentes. `.env.example` muestra `OCR_SERVICE_URL`, `BACKEND_AUTHORIZE_URL`, `BACKEND_FACE_MATCH_URL`, `TRACKER_PATH`, `FACE_MODEL_NAME` y `FACE_DETECTOR_BACKEND`. El archivo de muestra usa servicios locales; las URL desplegadas permanecen en la configuración/código existente. No incluir rostros, embeddings ni credenciales en GitHub/ZIP.

## Inicio local

Desde `Proyecto/`, una vez configurados los servicios necesarios y con el entorno actual:

```powershell
.\.venv\Scripts\python.exe -m uvicorn ai.main:app --host 127.0.0.1 --port 8001
```

Su Dockerfile usa **contexto `Proyecto/`**, copia `ai/` y toma `edge/models/yolo11n.pt` como peso YOLO11n para la imagen, sin requerir una copia adicional en la raíz:

```powershell
docker build -f ai/Dockerfile -t smartpark-ai .
```

El Dockerfile existente instala dependencias y precarga modelos durante el build; no se ejecutó en esta organización.

## Comprobación y rutas

`GET /health`, `GET /ready`, `POST /process`, `POST /face`, `POST /face/enroll`; además hay rutas de vehículo en `main.py`. `/ready` verifica preparación real de modelos y puede tardar. El flujo de `/process` consulta OCR y Backend; usar exclusivamente servicios y datos de prueba al validar. Revisar `ai/tests/` si existe y los contratos de `docs/audit/` antes de pruebas integradas.

## Errores frecuentes

La primera carga de DeepFace/RetinaFace puede ser lenta. Si falta un modelo, una URL o la compatibilidad CPU/CUDA, revisar el error exacto sin cambiar versiones de este proyecto. No ejecutar peticiones que alcancen AWS productivo durante pruebas locales.
