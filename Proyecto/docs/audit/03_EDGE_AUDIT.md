# 03. Auditoría Edge

## Linaje comprobado

`smartpark_edge_production.py:261` importa `edge_server_demo_gpu_model_detection_v3.py`, que importa `smartpark_gate_cloud` como módulo de nivel superior (`:265`). El único archivo observado está en `smartpark_edge_installer/`, ignorado por Git y fuera del path Python normal de raíz. El lanzador ajusta `edge.gate` y ejecuta `edge.gate.main()` (`:396-695`) **si se resuelve ese import**. `edge_server.py` también importa el núcleo, pero su captura usa detectores anteriores; no se encontró que el lanzador lo use. `smartpark_edge_installer/smartpark_edge.py` contiene una copia modificada de la rama de demo y es iniciada por `smartpark_launcher_release_v2.py` dentro del EXE. **No hay un único Edge autocontenido en Git**.

## Flujo real en código

```text
HC-SR04/ESP32 (`entradav2 (1).ino`, versión y compilación por verificar)
  → AWS IoT Core, topic smartpark/gates/gate-01/detection, MQTT/mTLS
  → smartpark_gate_cloud.on_mqtt_message, interceptado por servidor Edge
  → cv2.VideoCapture(CAMERA_SOURCE), cámara USB/DroidCam si Windows la expone
  → YOLO11n + ByteTrack, cruce de línea: arriba→abajo ENTRY; abajo→arriba EXIT
  → YuNet detecta cara, YOLOv8n especializado detecta placa
  → ventanas de frames válidos y nítidos; JPEG de los mejores frames
  → httpx POST multipart face_image + plate_image + event_type
  → Backend /api/v1/access/process → IA/OCR → autorización → IoT barrera
```

El núcleo define cámara 0 (`smartpark_gate_cloud.py:77`); el lanzador acepta `camera_source: auto` o un índice y prueba cámaras (`smartpark_edge_production.py:294-390,396-429`). DroidCam no aparece como SDK integrado: debe presentar un dispositivo de vídeo a OpenCV. YOLO se carga en el núcleo (`:194-198`); `model.track` usa la configuración ByteTrack. La línea virtual usa `LINE_POSITION=0.50`, margen 25 y estados por centro (`:491-687`). YuNet se carga en el servidor (`edge_server_demo_gpu_model_detection_v3.py:746-793`) con fallback Haar; el detector de placas se carga en `:807-830`. Umbrales de confianza, nitidez, conteo de frames y tiempos están en `:568-645`; calidad en `:841+`; captura facial/placa en `:1202+/:1755+`. La carga puede descargar modelos en tiempo de importación si faltan (`:651-813`): no se importó durante esta auditoría.

El firmware observado usa GPIO 5/18/19 para TRIG/ECHO/servo, umbral 20 cm y publica JSON con `device_id`, `event: VEHICLE_DETECTED`, `distance_cm`; se reconecta a Wi-Fi/MQTT y atiende comandos OPEN/CLOSE. El topic de detección coincide con el default Edge y el topic de comandos con el default Backend. `secrets.h` requerido no está presente. No se compiló ni se probó el sensor.

## Comunicación y operación

El núcleo configura mTLS con CA, certificado y clave (`smartpark_gate_cloud.py:378-405`) y se suscribe al topic de detección. Las rutas locales FastAPI del servidor son `/`, `/health`, `/status`, `/video` (MJPEG), `/demo/device`, `/demo/trigger` (`:2679-2751`). El lanzador elimina solo `/demo/trigger`, deja `/demo/device`. La API escucha en `127.0.0.1:9000`, por lo que GuardGate en la misma laptop puede consultarla. Edge envía HTTPS al valor `backend_url` del JSON, por defecto API Gateway; el núcleo conserva un antiguo ALB/IP HTTP que el lanzador reemplaza. El POST usa `httpx` desde el núcleo (`:1146-1200`); comprobar en una prueba el resultado y los reintentos. La elección AUTO/CPU/CUDA y el parche del dispositivo Ultralytics están en el servidor (`:105-256`); CUDA depende de la instalación local de PyTorch, no del nombre del archivo.

## Riesgos y duplicación

- `smartpark_gate_cloud.py` y todo `smartpark_edge_installer/` están ignorados por `.gitignore`: un clon no reproduce el Edge aunque `smartpark_edge_production.py` esté versionado.
- El servidor de demo y la copia del instalador tienen rutas similares y hashes distintos. Comparar diferencias funcionales antes de elegir una; el instalador además incluye simulación con tecla S.
- `edge_server.py` conserva otra API/captura; no se demuestra uso actual, pero puede ser útil como referencia histórica.
- Modelos y clave privada aparecen duplicados bit a bit en raíz e instalador. No distribuir la clave existente.
- Inicialización de modelos y cámara en import/arranque dificulta pruebas aisladas y puede descargar archivos. No se ejecutó.
- La mezcla de CORS permitido y navegador Amplify HTTPS → Edge HTTP localhost requiere prueba real de navegador (incluye políticas de acceso a red local).

## PROPUESTA DE EDGE CANÓNICO

Tomar como **candidato** la ruta `smartpark_edge_production.py` → servidor V3 → núcleo `smartpark_gate_cloud.py`, porque la dependencia está explícita y permite sensor real con configuración. Antes de reorganizar: (1) recuperar/versionar de forma segura el núcleo sin certificados; (2) comparar funcionalmente `smartpark_edge_installer/smartpark_edge.py` y el ejecutable; (3) ejecutar una prueba con cámara, modelo, MQTT y Backend; (4) decidir si conservar un modo demo opcional separado. No se cambió código.
