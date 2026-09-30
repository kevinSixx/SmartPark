# OCR

Servicio FastAPI `ocr/main.py` en el puerto 8002 (versión 1.1.0). Recibe imágenes en `POST /plate`, aplica preprocesamiento y usa PaddleOCR en CPU; normaliza la matrícula antes de responder. `GET /health` informa salud. `plate_recognition.py` permanece como archivo existente, sin cambiar su estado ni sustituir el punto de entrada.

## Estado actual y dependencias

`requirements.txt` y `Dockerfile` actuales se conservan exactamente. Incluyen el conjunto vigente de PaddleOCR, PyMuPDF, NumPy, OpenCV, FastAPI y Uvicorn según los archivos del proyecto. No se modernizaron ni reinstalaron paquetes. `main.py` no lee variables de entorno propias; `.env.example` lo aclara. El motor OCR se inicializa al importar el módulo, por lo que el inicio puede tardar y depender de modelos ya disponibles.

## Inicio local

Desde `Proyecto/`, usando el `.venv` actual:

```powershell
.\.venv\Scripts\python.exe -m uvicorn ocr.main:app --host 127.0.0.1 --port 8002
```

El Dockerfile original usa **contexto `Proyecto/ocr/`**:

```powershell
docker build -f ocr/Dockerfile -t smartpark-ocr ocr
```

Ese build no se ejecutó durante esta organización. La imagen base y todas las versiones siguen como estaban.

## Comprobación

Con un servicio aislado iniciado, consultar `GET /health` y enviar a `POST /plate` un archivo de prueba autorizado. No usar imágenes personales reales en el repositorio ni en evidencias públicas.

## Errores frecuentes

Una falla durante importación suele implicar dependencias o modelos PaddleOCR ausentes. Una lectura deficiente requiere revisar iluminación y calidad de la imagen antes de tocar umbrales o lógica. Registrar cualquier bloqueo de entorno sin cambiar versiones.
