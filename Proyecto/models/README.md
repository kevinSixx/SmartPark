# Modelos de SmartPark

Estos pesos forman parte del proyecto y deben conservarse en Git. Los dos archivos de `models/smartpark/` ocupan aproximadamente 0,23 MB (`face_detection_yunet_2023mar.onnx`) y 6,25 MB (`license_plate_yolov8n.pt`). Las copias de `edge/models/smartpark/` y `smartpark_edge_installer/models/smartpark/` tienen el mismo contenido. `edge/models/yolo11n.pt` y `smartpark_edge_installer/yolo11n.pt` son copias del tercer peso (aproximadamente 5,61 MB). No se requiere una descarga externa para estos tres modelos si se incluyen las rutas citadas en el commit final.

El `ai/Dockerfile` copia `edge/models/yolo11n.pt` desde el contexto `Proyecto/` a `/app/yolo11n.pt`, que es la ruta usada dentro de la imagen. El build ya no depende de un peso adicional en la raíz. Ejecute `docker build -f ai/Dockerfile -t smartpark-ai .` desde `Proyecto/` una vez que `edge/models/yolo11n.pt` forme parte del commit final. Revise también la licencia y procedencia de cada peso antes de publicar el repositorio.

Los modelos bajo `backend/app/models/` son código Python de base de datos y se conservan por separado. No se ignora la carpeta `models/` ni las extensiones `.pt` y `.onnx`.
