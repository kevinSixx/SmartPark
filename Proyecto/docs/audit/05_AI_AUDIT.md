# 05. Auditoría IA

`ai/main.py` es FastAPI 2.8.1; `ai/Dockerfile` inicia Uvicorn en 8001 desde contexto raíz. `/health` informa configuración/estado; `/ready` devuelve 503 si el calentamiento facial falla y 200 cuando está listo (`main.py:1008-1045`). En startup se ejecuta `warmup_face_models` en threadpool y la app espera su finalización (`:545-620`). Inferencias faciales se serializan por proceso con `asyncio.Lock` y se envían a threadpool (`:172-176,739`). Una instancia nueva puede tardar considerablemente en estar lista; `/health` no equivale a `/ready`.

| Categoría | Componente | Evidencia |
|---|---|---|
| Modelo | YOLO11n pesos `yolo11n.pt` | `vehicle_detection.py:104`; Docker copia a `/app/yolo11n.pt` |
| Modelo | ArcFace | `FACE_MODEL_NAME='ArcFace'`, `DeepFace.represent` en `main.py:331,574` |
| Modelo/detector | RetinaFace | `FACE_DETECTOR_BACKEND='retinaface'` en `main.py:150`; `DeepFace.represent` |
| Framework | DeepFace | API que prepara detector y embeddings; no es un modelo único |
| Librerías | TensorFlow, Ultralytics, OpenCV, NumPy, FastAPI, httpx | `requirements.txt`, imports |
| Lógica propia | Normalización L2, control de una sola cara, promedio de 3–5 embeddings, match remoto, orquestación OCR/autorización | `main.py:225+`, `:1058+`, `:2358+` |

Rutas: `GET /health`, `GET /ready`, `POST /face/enroll`, `/face`, `/face-legacy`, `/vehicle`, `/vehicle-track`, `/process`. `/face` genera embedding y llama Backend `/api/v1/face-profiles/match`; `/face/enroll` devuelve embedding agregado al Backend. `/process` recibe dos imágenes y ENTRY/EXIT, llama OCR `/plate` mediante `OCR_SERVICE_URL`, reconoce rostro y llama Backend `/api/v1/access/authorize` mediante `BACKEND_AUTHORIZE_URL`. `BACKEND_FACE_MATCH_URL` apunta a Backend `/api/v1/face-profiles/match`. Umbral de similitud decisivo está en Backend `services/face_profiles.py` (`FACE_MATCH_THRESHOLD`, default 0.70), no atribuirlo al modelo AI. `ai/face_recognition.py` implementa otra ruta de reconocimiento usada por `/face-legacy`; `ai/plate_recognition.py` contiene PaddleOCR local y **sí** se importa desde `ai/smartpark_demo_local.py`. `ai/vehicle_tracking.py` carga otra instancia YOLO y no tiene referencia estática localizada; revisar scripts, usos directos e historial antes de clasificarlo como redundante.

El Dockerfile usa Python 3.11 slim, precarga ArcFace/RetinaFace durante build, copia YOLO11n y expone 8001. Esa precarga depende de red o caché de modelos: reproducibilidad requiere fijar hashes/licencias y documentar caché. La imagen etiquetada `smartpark-ai:2.8.1-cpu` consta en contexto de entrega, pero no se halló un manifiesto ECR ni tag en el Dockerfile. El código no obliga CUDA; la imagen y TensorFlow parecen orientados a CPU. No se importó AI ni se descargaron pesos durante la auditoría.
