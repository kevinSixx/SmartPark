# Edge organizado (copia de trabajo)

Esta carpeta reúne **copias** del launcher operativo `smartpark_edge_production.py`, el servidor V3 `edge_server_demo_gpu_model_detection_v3.py` y `smartpark_gate_cloud.py`. Los originales de `Proyecto/` y `Proyecto/smartpark_edge_installer/` siguen presentes. El launcher inicia el modo de sensor real, cámara/DroidCam, YOLO11n + ByteTrack, línea ENTRY/EXIT, selección CPU/CUDA y comunicación MQTT/mTLS con IoT. El servidor añade detección local con YuNet y detector de matrícula YOLOv8n, mejor frame, API local y envío multipart al Backend. No se alteraron umbrales ni algoritmos.

## Archivos

`models/` contiene copias byte a byte de los tres modelos; `bytetrack_smartpark.yaml` es una copia del YAML de `ai/`. `installer/` contiene solo fuentes `.py`, `.ps1`, `.spec`, `.iss` y README anteriores. El empaquetado no se modificó ni se probó; varios scripts del instalador aún referencian la disposición original. Ver [cambios de rutas](../docs/reorganization/EDGE_PATH_CHANGES.md).

## Configuración y dependencias

El Edge usa el `.venv` existente de `Proyecto/`, con OpenCV, Ultralytics, PyTorch, HTTPX y AWS IoT SDK si ya están disponibles. No se creó ni actualizó un `requirements.txt`. `smartpark_edge_config.example.json` tiene las claves actuales del launcher sin certificados privados. Para una ejecución aislada futura, copiarlo localmente a `edge/smartpark_edge_config.json`, configurar cámara/Backend y colocar los certificados privados en `edge/certs/camera/` según esas rutas. El JSON activo y los certificados están ignorados por Git. La URL del endpoint IoT sigue definida en el código histórico de `smartpark_gate_cloud.py`; **el ejemplo JSON no la sustituye**. Verificar conectividad y destino antes de encender el Edge para evitar mensajes en el entorno real.

## Inicio y comprobación futura

Desde `Proyecto/`, después de revisar la configuración y con hardware/servicios de prueba:

```powershell
.\.venv\Scripts\python.exe edge\smartpark_edge_production.py
```

El launcher trabaja con la carpeta del propio script; las tres rutas ajustadas en la copia localizan modelos y tracker sin depender del directorio de trabajo. Mantiene el puerto **9000** y `GET /health`, `GET /status`, `GET /video`. El servidor V3 conserva también rutas de demostración, que no son el modo operativo del launcher. No se arrancó Edge en esta fase: importar el módulo puede cargar modelos, cámara y recursos IoT.

## Errores frecuentes

Un error de certificado/cámara apunta a la configuración local o hardware. Si falla CUDA, confirmar el soporte de PyTorch ya instalado sin cambiar versiones. Si falta un modelo, comparar su SHA-256 con el informe de organización. La compilación o ejecución del instalador permanece pendiente; no colocar claves IoT dentro del EXE ni de un ZIP público.
