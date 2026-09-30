# 09. Modelos y artefactos de inferencia

Tamaños observados localmente el 2026-09-29. No se descargó ni cargó ningún modelo. «ZIP» supone un paquete de **fuente reproducible**; una distribución de ejecutable requiere análisis de licencia y datos por separado.

| Ruta | Tamaño | Tipo | Uso/código de carga | Obligatorio | Origen | Licencia documentada | ZIP |
|---|---:|---|---|---|---|---|---|
| `yolo11n.pt` | 5,613,764 B | pesos YOLO11n | `ai/vehicle_detection.py:104`, `smartpark_gate_cloud.py:197`; `ai/Dockerfile:74` copia | Sí para detección/tracking | Archivo presente; verificar origen/hash | No hallada en repo | DEPENDE de licencia y modo offline |
| `models/smartpark/face_detection_yunet_2023mar.onnx` | 232,589 B | YuNet ONNX | `edge_server_demo_gpu_model_detection_v3.py:536,746-793` | Sí para captura YuNet; fallback Haar existe | Archivo presente; código tiene URLs de descarga | No hallada | DEPENDE |
| `models/smartpark/license_plate_yolov8n.pt` | 6,245,603 B | YOLOv8n especializado en placa | `edge_server_demo_gpu_model_detection_v3.py:540,807-830` | Sí para detector especializado | Presente; código tiene URLs de descarga | No hallada | DEPENDE |
| `smartpark_edge_installer/yolo11n.pt` | 5,613,764 B | copia exacta (SHA-256 coincide) | `SmartParkEdge_v2.spec` y núcleo instalado | Para instalador empaquetado | Copia local | No hallada | NO, si se empaqueta fuente canónica una sola vez |
| `smartpark_edge_installer/models/smartpark/face_detection_yunet_2023mar.onnx` | 232,589 B | copia exacta | Instalable | Para EXE | Copia local | No hallada | NO en ZIP fuente |
| `smartpark_edge_installer/models/smartpark/license_plate_yolov8n.pt` | 6,245,603 B | copia exacta | Instalable | Para EXE | Copia local | No hallada | NO en ZIP fuente |
| ArcFace y RetinaFace | No se halló peso/caché de aplicación fuera de entornos/builds | modelos faciales | `DeepFace.represent` en `ai/main.py:331,574`; `ai/Dockerfile:81-96` precarga | Sí para IA facial | Descarga/caché de DeepFace en build/startup | No hallada | DEPENDE: manifestar versión/hash o incluir legalmente |
| PaddleOCR modelos | No se halló paquete de pesos independiente en fuente | modelos OCR | `ocr/main.py:50` crea `PaddleOCR`; imagen/caché puede descargarlos | Sí para OCR | Dependencia o caché generada | No hallada | DEPENDE de estrategia offline |
| `ai/faces/kevin_embedding.npy` y fotos de `ai/faces/` | Ver inventario | datos biométricos, no pesos generales | `ai/smartpark_demo_local.py`/scripts de prueba: verificar | No para servicio cloud actual | Datos de personas | No hallada | NO |

No se encontró `LP.pt` con ese nombre físico: el comentario del instalador lo menciona, pero el archivo real es `license_plate_yolov8n.pt`. La presencia de URL de descarga no garantiza disponibilidad, integridad o permiso de redistribución. Registrar SHA-256 completo, fuente, licencia, versión de librería y uso previsto antes de construir ZIP final.
