# Decisión Edge (2026-09-29)

## Comparación y fuente canónica

La ruta operativa confirmada por el responsable era `smartpark_edge_production.py` → `edge_server_demo_gpu_model_detection_v3.py` → `smartpark_gate_cloud.py`. Ahora vive en `edge/app/` con los mismos nombres para facilitar comparación y reducir riesgo de imports. El lanzador se invoca con `python -m edge.app.smartpark_edge_production`. Configura cámara auto/índice, backend, topic/certificados y CPU/CUDA; inicia FastAPI :9000 en hilo y ejecuta `gate.main()` real. Desactiva `/demo/trigger`.

La ruta del EXE era `smartpark_launcher_release_v2.py` → `smartpark_edge.py` → `smartpark_gate_cloud.py`. La comparación de servidor V3 y `smartpark_edge.py` dio **2.861 líneas idénticas al normalizar CRLF/LF**; sus SHA-256 de bytes diferían solo por saltos de línea (`6203B554...` frente a `95B4DF41...`). Por eso `edge/installer/smartpark_edge.py` es ahora un adaptador al servidor canónico, y no mantiene otra copia funcional. El original byte a byte permanece en el respaldo local ignorado `Proyecto/smartpark_edge_installer/smartpark_edge.py`. El núcleo `gate_cloud` es único en el árbol fuente y lo comparten ambas rutas.

## Funciones y diferencias conservadas

El servidor común conserva `/health`, `/status`, `/video`, `/demo/device`, `/demo/trigger`; OpenCV/MJPEG, selección AUTO/CPU/CUDA, YuNet, YOLOv8n de matrícula, ventanas de best frame y sharpness, y puente con `gate`. El núcleo conserva MQTT/mTLS, YOLO11n/ByteTrack, línea ENTRY/EXIT, captura, POST multipart y :9000 mediante el servidor. `edge_server.py` anterior está en `edge/legacy/` y no forma parte del launcher; usa captura anterior y queda **REQUIERE_VERIFICACION** antes de retirarlo.

Los lanzadores **no son equivalentes**. El de fuente lee JSON, usa sensor real y desactiva disparo demo. La GUI del instalador guarda preferencias en `%LOCALAPPDATA%`, selecciona cámara/garita, ejecuta `gate.main()` y permite `S` en la ventana de video para simulación. No se fusionó esa lógica. Mantener ambos preserva las capacidades observadas sin cambiar algoritmos.

## Recursos, paths y empaquetado

Antes, el import de `smartpark_gate_cloud` fallaba en un clon por estar bajo una carpeta ignorada. Ahora hay imports de paquete `edge.app`. `edge/models/` contiene los tres pesos únicos del árbol publicable; SHA-256 coincide con las antiguas copias del instalador. El tracker Edge es una copia del YAML AI en `edge/app/`; AI conserva el suyo. Las rutas de pesos se resuelven desde el módulo o `_MEIPASS`; la configuración JSON privada define cámara, backend y rutas de certificados. `SmartParkEdge_v2.spec` toma código/modelos/tracker de la fuente canónica y omite certificados/clave. El launcher GUI exige provisionarlos en `%LOCALAPPDATA%\SmartParkUCE\certs\camera\`. Los scripts `.ps1`/`.iss` se conservaron y no se ejecutaron.

## Verificación pendiente

**REQUIERE_VERIFICACION:** import/arranque en Windows con dependencias y cámara, CPU/CUDA, conexión MQTT con certificados nuevos, POST al Backend local, `GET /health|status|video`, build PyInstaller, instalación Inno en PC limpia y simulación `S` frente a sensor real. El empaquetado puede necesitar ajustes de hooks/rutas no detectables por compilación estática. No se distribuye el EXE histórico: puede contener una clave IoT anterior.

