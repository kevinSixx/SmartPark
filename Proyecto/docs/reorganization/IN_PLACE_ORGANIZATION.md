# Organización dentro de Proyecto/

Fecha: 2026-09-30. **Raíz funcional: `SmartPark/Proyecto/`**. La recuperación anterior ya estaba completa; este trabajo no volvió a restaurar ni movió archivos fuera de `Proyecto/`.

## Carpetas y archivos nuevos

- `edge/` con tres scripts principales (nombres originales), `models/`, `installer/`, YAML de ByteTrack, configuración pública de ejemplo y README.
- `firmware/esp32/` con copia exacta de `entradav2 (1).ino`, ejemplo de `secrets.h` y README.
- `infra/` con README descriptivo. `docker-compose.yml` sigue en la raíz.
- `docs/architecture/`, `docs/api/`, `docs/installation/`, `docs/testing/`, `docs/evidence/`, `docs/costs/`, `docs/audit/`, `docs/reorganization/` se mantienen o se crearon vacías según necesidad; los archivos de auditoría previos se conservaron.
- README y `.env.example` en `backend/`, `ai/`, `ocr/`, `frontend/` (el README genérico de Vite en Frontend se sustituyó por documentación SmartPark). README principal de `Proyecto/` actualizado. `.gitignore` de `Proyecto/` ampliado para futura entrega.

## Copias realizadas

| Origen original dentro de `Proyecto/` | Copia |
| --- | --- |
| `smartpark_edge_production.py` | `edge/smartpark_edge_production.py` |
| `edge_server_demo_gpu_model_detection_v3.py` | `edge/edge_server_demo_gpu_model_detection_v3.py` |
| `smartpark_edge_installer/smartpark_gate_cloud.py` | `edge/smartpark_gate_cloud.py` |
| `yolo11n.pt` | `edge/models/yolo11n.pt` |
| `models/smartpark/face_detection_yunet_2023mar.onnx` | `edge/models/smartpark/face_detection_yunet_2023mar.onnx` |
| `models/smartpark/license_plate_yolov8n.pt` | `edge/models/smartpark/license_plate_yolov8n.pt` |
| `ai/bytetrack_smartpark.yaml` | `edge/bytetrack_smartpark.yaml` |
| `entradav2 (1).ino` | `firmware/esp32/entradav2 (1).ino` |

En `edge/installer/` se copiaron, sin editar: `smartpark_edge.py`, `smartpark_gate_cloud.py`, `smartpark_launcher_release_v2.py`, `build_smartpark_exe_v2.ps1`, `crear_instalador_final.ps1`, `crear_instalador_final_v2.ps1`, `crear_instalador_final_v3.ps1`, `SmartParkEdge.iss`, `SmartParkEdge_Final.iss`, `SmartParkEdge_v2.spec`, `README_INSTALADOR_FINAL.txt` y `README_SMARTPARK_V2.txt`. No se copiaron `build/`, `dist/`, EXE, RAR, claves ni certificados. Los scripts fuente del instalador no se ajustaron y su funcionamiento desde la nueva ruta sigue pendiente de prueba.

## Originales y código preservados

Siguen presentes `smartpark_edge_production.py`, `edge_server_demo_gpu_model_detection_v3.py`, `edge_server.py`, `smartpark_edge_config.json`, `smartpark_edge_installer/`, `models/`, `yolo11n.pt` y `entradav2 (1).ino` en la raíz original. Backend (`app/`, `migrations/`, `tests/`), IA, OCR y el código de Frontend no se movieron ni editaron en esta fase. Se respetaron los cambios de Frontend que ya existían antes de comenzar. `Proyecto/.venv/` permaneció en el mismo lugar y no se instaló nada.

Las únicas líneas de código cambiadas están en **dos copias Edge** y se detallan en [EDGE_PATH_CHANGES.md](EDGE_PATH_CHANGES.md). El firmware copiado, el launcher copiado, los modelos y el YAML de ByteTrack conservan SHA-256. `backend/requirements.txt`, `ai/requirements.txt`, `ocr/requirements.txt`, tres Dockerfiles, `frontend/package.json`, `frontend/package-lock.json` y `docker-compose.yml` no se modificaron.

## SHA-256 de modelos, origen = copia

| Modelo | SHA-256 |
| --- | --- |
| YOLO11n `yolo11n.pt` | `0EBBC80D4A7680D14987A577CD21342B65ECFD94632BD9A8DA63AE6417644EE1` |
| YuNet `face_detection_yunet_2023mar.onnx` | `8F2383E4DD3CFBB4553EA8718107FC0423210DC964F9F4280604804ED2552FA4` |
| Matrícula `license_plate_yolov8n.pt` | `B7557890BF829BD0B694A6A684E30599EF0E588F305397106158C958A08DAD08` |

Firmware origen = copia: `01C1FCA86919C10B553719D2B5A7481CDCDB2F5D06CA4666A104DEFC1310B367`.

## GitHub, ZIP y seguridad

`.gitignore` excluye entornos, `node_modules`, cachés, compilados, `.env`, `secrets.h`, claves, certificados, biometría, imágenes de debug y ZIP/RAR/EXE. También mantiene ignorados **solo en la raíz original** los scripts Edge antiguos y `smartpark_edge_installer/`; la copia `edge/` queda visible para Git. El ignore no borra archivos locales ni retira archivos ya rastreados.

**Bloqueo para GitHub público:** `git ls-files` todavía muestra `Proyecto/.env`, `Proyecto/frontend/.env`, `Proyecto/certs/camera/camera-private.pem.key`, el certificado de cámara, fotos bajo `Proyecto/ai/faces/`, `Proyecto/ai/faces/kevin_embedding.npy`, ZIP/RAR y archivos de `Proyecto/node_modules/`. No se leyó ni imprimió el contenido de secretos. La entrega pública requiere retirar esos archivos del índice, revisar/sanear el historial y rotar cualquier credencial previamente versionada. Estas acciones no están autorizadas dentro de esta organización y no se hicieron. No se alteró Git remoto ni se borraron archivos locales.

## Comprobaciones de esta fase

| Comprobación | Resultado |
| --- | --- |
| `.venv/Scripts/python.exe --version` | Python 3.11.9; ejecutable con el mismo SHA-256 inicial `21BB438C0D4A6F1F164B9A646F6EE000340185E5871180AEC06DB8D3F07C0082` |
| `.venv/Scripts/python.exe -m compileall -q Proyecto/backend Proyecto/ai Proyecto/ocr Proyecto/edge` | PASS, código de salida 0; no se importaron servicios |
| `importlib.util.find_spec` con el Python de `.venv` | PASS para FastAPI, Uvicorn, SQLAlchemy, psycopg, OpenCV, Ultralytics, AWS CRT/IoT, DeepFace, PaddleOCR y módulos SmartPark; solo confirma disponibilidad de módulos |
| SHA-256 de los tres modelos, firmware, launcher y YAML de ByteTrack | PASS, copias iguales a los originales |
| SHA-256 de las 12 fuentes copiadas del instalador | PASS, cada copia igual al original |
| `npm run build` en Frontend con `node_modules` existente | PASS, Vite v8.3.1; `dist/` generado localmente e ignorado |
| JSON de ejemplo Edge | PASS, sintaxis válida |
| Backend/IA/OCR/Edge activos, firmware, instalador y AWS | NO EJECUTADO por alcance de esta fase |

Los hashes iniciales/finales de `backend`, `ai` y `ocr` `requirements.txt`/Dockerfile, `frontend/package.json`/`package-lock.json`, `.venv/Scripts/python.exe`, firmware y scripts Edge originales coincidieron. El build no instaló dependencias. No se arrancaron OCR, IA, Backend o Edge; no se compiló firmware/instalador ni se tocó AWS.

En una comparación manual se transcribió inicialmente el hash esperado de `ocr/requirements.txt` sin su último carácter. Se verificó de nuevo el hash completo y `git diff` de ese archivo: ambos confirmaron que no cambió.

## Pruebas siguientes, en orden

1. Revisar que los `.env` privados, `edge/smartpark_edge_config.json` y certificados apunten a **recursos aislados**, nunca producción.
2. Ejecutar pruebas locales de Backend con base PostgreSQL de prueba y `GET /health`/`GET /db-check`.
3. Iniciar OCR en :8002 y probar `/health` y `/plate` con imagen sintética/autorizada.
4. Iniciar IA en :8001 y probar `/health`, `/ready`, `/face` y `/process` contra Backend/OCR locales.
5. Iniciar Frontend en desarrollo, verificar navegación, Backend y vídeo Edge; ejecutar sus tests y lint.
6. Validar la copia Edge en banco de pruebas: cámara, CPU/GPU, modelos, MQTT de laboratorio y `/health`, `/status`, `/video` en :9000.
7. Validar firmware con ESP32 y barrera de laboratorio; después revisar y probar PyInstaller/Inno Setup del instalador con la estructura nueva.
8. Tomar capturas reales para `docs/evidence/`, verificar licencias de modelos y **retirar del índice/sanear historial y rotar credenciales ya versionadas** antes del ZIP/GitHub público.
