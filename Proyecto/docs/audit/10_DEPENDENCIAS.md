# 10. Dependencias

| Módulo | Manifiesto | Aislamiento actual | Hallazgos |
|---|---|---|---|
| EDGE | No hay `requirements.txt` específico en raíz ni instalador | **No independiente** desde Git: núcleo ignorado, usa paquetes compartidos/venv local | Requiere OpenCV, NumPy, FastAPI/Uvicorn, httpx, Ultralytics, Torch, AWS IoT Device SDK y posiblemente `lap`; declarar versiones/Windows/CUDA por separado |
| BACKEND | `backend/requirements.txt` | Instalable desde raíz con Python 3.11 y DB/secret configurados | FastAPI 0.141.1, SQLAlchemy 2.0.54, psycopg 3.3.6, Alembic 1.20.0, JWT, boto3, paho-mqtt, httpx; `paho-mqtt` no aparece importado en `backend/app` (IoT usa boto3), revisar antes de retirar |
| AI | `ai/requirements.txt` | Imagen usa contexto raíz y peso raíz; paquete Python aislable con recursos externos | Fija DeepFace/RetinaFace/TensorFlow/NumPy/OpenCV pero deja `ultralytics`, `fastapi`, `httpx`, `boto3`, `Pillow` sin versión. `boto3` no tiene import directo localizado en `ai/`; `ai/plate_recognition.py` y pruebas usan `paddleocr` aunque el manifiesto AI no lo declara: los demos no son instalables con solo requirements AI |
| OCR | `ocr/requirements.txt` | Sí como imagen si contexto es `ocr/` y base Paddle disponible | PaddleOCR 2.7.0.3 sobre Paddle 2.6.2, PyMuPDF 1.20.0, NumPy 1.26.4; FastAPI/Uvicorn/OpenCV/Pillow sin pin. Compatibilidad necesita build real |
| FRONTEND | `frontend/package.json` + lock | Sí, con Node/npm compatibles con Vite 8 | `package.json` de raíz duplica solo dos dependencias y genera `node_modules/` raíz; no ejecuta Vite. Falta rango Node documentado y `.env.example` útil |

No se halló `pyproject.toml`. `backend/Dockerfile` y `ai/Dockerfile` dependen del contexto raíz; OCR depende de contexto de subcarpeta. No se ejecutó `pip freeze` porque el entorno `.venv` no prueba instalación reproducible y leer miles de paquetes aporta poco a la fuente; tampoco `npm list` ni instalación. **Versiones incompatibles confirmadas: ninguna sin resolver dependencias/build.** Riesgos concretos: TensorFlow/`tf-keras` con DeepFace, PaddleOCR con base Paddle, OpenCV con NumPy y versiones transitivas sin fijar. Los imports usados/no declarados se deben validar por entorno con `pip check`, instalación limpia y prueba de import en copia/CI; la lista Edge es el faltante inequívoco.

Para fijar dependencias futuras, separar `edge/requirements.txt` de `ai/requirements.txt`, mover dependencias solo de demo a extra `dev`, congelar lock o constraints por imagen y documentar Python 3.11, CUDA/CPU y Node. No se cambió ningún manifiesto.
