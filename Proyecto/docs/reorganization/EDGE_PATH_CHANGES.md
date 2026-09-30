# Cambios de rutas de la copia Edge

Fecha: 2026-09-30. Los originales en la raíz de `Proyecto/` y en `smartpark_edge_installer/` no se modificaron.

| Archivo copiado | Cambio mínimo | Motivo |
| --- | --- | --- |
| `edge/smartpark_gate_cloud.py` | `YOLO_MODEL_PATH` apunta a `Path(__file__).resolve().parent / "models" / "yolo11n.pt"` | usar la copia de YOLO11n en `edge/models/` con independencia del directorio de trabajo |
| `edge/smartpark_gate_cloud.py` | primera opción del tracker: `Path(__file__).resolve().parent / "bytetrack_smartpark.yaml"` | usar el YAML copiado; se mantienen las opciones antiguas y el fallback |
| `edge/edge_server_demo_gpu_model_detection_v3.py` | valor por defecto de `SMARTPARK_LOCAL_MODELS_DIR` relativo al archivo: `edge/models/smartpark/` | usar las copias YuNet y YOLOv8n, sin depender de la carpeta desde la que se inicia Python |

`edge/smartpark_edge_production.py` y todos los archivos bajo `edge/installer/` son copias byte a byte. Los tres imports principales conservan sus nombres y ahora están en una misma carpeta. No se cambiaron endpoints, topics, thresholds, modelos, puertos, algoritmos ni lógica ENTRY/EXIT. `smartpark_edge_config.example.json` solo refleja el esquema del launcher; el JSON de configuración real no fue copiado. El launcher busca `edge/smartpark_edge_config.json` y resuelve rutas de certificados privadas respecto a `edge/`. El ejemplo no permite redefinir el endpoint IoT hardcodeado en el gate histórico, por lo que hay que verificar ese destino antes de cualquier ejecución.

**Pendiente:** ejecución aislada de Edge y validación del instalador. Los `.spec`, `.iss` y `.ps1` copiados pueden seguir referenciando el árbol antiguo; no se editaron por la instrucción de conservar el instalador. Su empaquetado necesita una revisión posterior que confirme qué fuente y modelos incluye, sin certificados privados.
