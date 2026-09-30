"""
SmartPark UCE - Edge Demo GPU/CPU + Real Face/Plate Detection
=====================================================

Archivo alternativo para demostraciones.

NO reemplaza:
    - smartpark_gate_cloud.py
    - edge_server.py

Requisitos:
    - Este archivo debe estar en la misma carpeta que smartpark_gate_cloud.py.
    - Deben seguir existiendo y estar configurados los certificados, YOLO, cámara
      y demás recursos que ya usa smartpark_gate_cloud.py.
    - Para usar GPU NVIDIA, PyTorch debe haber sido instalado con soporte CUDA.

Qué agrega:
    1. Selección AUTO / CPU / GPU (CUDA).
    2. Inyección del dispositivo elegido a las inferencias de Ultralytics/YOLO.
    3. Tecla S para simular el evento VEHICLE_DETECTED del HC-SR04.
    4. Endpoint POST /demo/trigger para simular el sensor desde HTTP.
    5. Estado de CPU/GPU en /health, /status y /demo/device.
    6. Mantiene el procesamiento real hacia AWS:
       Edge -> API Gateway -> ALB -> Backend -> IA/RDS/IoT.

Ejemplos:
    python edge_server_demo_gpu.py
    python edge_server_demo_gpu.py --device auto
    python edge_server_demo_gpu.py --device cpu
    python edge_server_demo_gpu.py --device cuda

Variables opcionales:
    SMARTPARK_DEVICE=auto|cpu|cuda|cuda:0
    SMARTPARK_DEMO_DISTANCE_CM=12.0
    SMARTPARK_BACKEND_URL=https://2uz85rgfg7.execute-api.us-east-1.amazonaws.com
    SMARTPARK_SHOW_WINDOW=true
"""

from __future__ import annotations

from collections import deque
import argparse
import json
import os
import platform
import sys
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any


# ============================================================
# CONFIGURACIÓN TEMPRANA DEL DISPOSITIVO
# ============================================================

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SmartPark UCE Edge Demo - CPU/GPU + sensor simulado"
    )
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default=None,
        help="Dispositivo de inferencia: auto, cpu o cuda.",
    )
    parser.add_argument(
        "--no-menu",
        action="store_true",
        help="No mostrar selector interactivo al iniciar.",
    )
    return parser.parse_args()


def _interactive_device_menu(default_mode: str) -> str:
    if not sys.stdin.isatty():
        return default_mode

    print()
    print("=" * 72)
    print("SMARTPARK UCE - MODO DE PROCESAMIENTO")
    print("=" * 72)
    print("  [1] AUTO  - usa GPU NVIDIA si CUDA está disponible")
    print("  [2] CPU   - fuerza procesamiento en CPU")
    print("  [3] GPU   - intenta usar NVIDIA CUDA")
    print()
    print(f"Valor por defecto: {default_mode.upper()}")
    print("Presiona ENTER para usar el valor por defecto.")
    print()

    try:
        value = input("Selecciona 1, 2 o 3: ").strip()
    except (EOFError, KeyboardInterrupt):
        return default_mode

    return {
        "1": "auto",
        "2": "cpu",
        "3": "cuda",
        "": default_mode,
    }.get(value, default_mode)


ARGS = _parse_args()

ENV_DEVICE = (
    os.getenv("SMARTPARK_DEVICE", "auto")
    .strip()
    .lower()
)

if ENV_DEVICE not in {"auto", "cpu", "cuda", "cuda:0"}:
    ENV_DEVICE = "auto"

REQUESTED_MODE = ARGS.device or ENV_DEVICE

if ARGS.device is None and not ARGS.no_menu:
    REQUESTED_MODE = _interactive_device_menu(REQUESTED_MODE)


# Si el usuario fuerza CPU, ocultamos CUDA antes de importar torch/Ultralytics.
if REQUESTED_MODE == "cpu":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""


# ============================================================
# IMPORTS DE PROCESAMIENTO
# ============================================================

import cv2
import numpy as np
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


try:
    import torch
except Exception as exc:
    raise RuntimeError(
        "No se pudo importar PyTorch. "
        "SmartPark necesita torch/ultralytics para YOLO."
    ) from exc


def _resolve_compute_device(requested: str) -> dict[str, Any]:
    cuda_available = bool(torch.cuda.is_available())

    gpu_name = None
    gpu_memory_gb = None

    if cuda_available:
        try:
            gpu_name = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            gpu_memory_gb = round(
                props.total_memory / (1024 ** 3),
                2,
            )
        except Exception:
            gpu_name = "GPU NVIDIA / CUDA"
            gpu_memory_gb = None

    normalized = requested.lower().strip()

    if normalized in {"cuda", "cuda:0"}:
        if cuda_available:
            selected = "cuda:0"
            effective_mode = "GPU"
            fallback = False
        else:
            selected = "cpu"
            effective_mode = "CPU"
            fallback = True

    elif normalized == "cpu":
        selected = "cpu"
        effective_mode = "CPU"
        fallback = False

    else:
        if cuda_available:
            selected = "cuda:0"
            effective_mode = "GPU"
        else:
            selected = "cpu"
            effective_mode = "CPU"
        fallback = False

    if selected.startswith("cuda"):
        try:
            torch.backends.cudnn.benchmark = True
        except Exception:
            pass

    return {
        "requested": normalized,
        "selected": selected,
        "mode": effective_mode,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "gpu_memory_gb": gpu_memory_gb,
        "fallback": fallback,
        "torch_version": getattr(torch, "__version__", "unknown"),
        "cuda_version": getattr(torch.version, "cuda", None),
    }


DEVICE_INFO = _resolve_compute_device(REQUESTED_MODE)
COMPUTE_DEVICE = DEVICE_INFO["selected"]


# ============================================================
# FORZAR DISPOSITIVO EN ULTRALYTICS
# ============================================================

def _patch_ultralytics_device(device: str) -> bool:
    """
    Inyecta device=... en Model.predict().

    Esto cubre:
      - model(...)
      - model.predict(...)
      - model.track(...), porque track termina usando predict()

    No modifica smartpark_gate_cloud.py.
    """
    try:
        from ultralytics.engine.model import Model as UltralyticsModel
    except Exception as exc:
        print(
            "[DEVICE] No se pudo importar Ultralytics para aplicar "
            f"el dispositivo: {exc}"
        )
        return False

    if getattr(UltralyticsModel.predict, "_smartpark_device_patch", False):
        return True

    original_predict = UltralyticsModel.predict

    def smartpark_predict(self, *args, **kwargs):
        kwargs.setdefault("device", device)
        return original_predict(self, *args, **kwargs)

    smartpark_predict._smartpark_device_patch = True
    smartpark_predict._smartpark_original = original_predict

    UltralyticsModel.predict = smartpark_predict
    return True


ULTRALYTICS_DEVICE_PATCHED = _patch_ultralytics_device(
    COMPUTE_DEVICE
)


# ============================================================
# IMPORTAR CORE EXISTENTE
# ============================================================

try:
    import smartpark_gate_cloud as gate
except Exception as exc:
    raise RuntimeError(
        "No se pudo importar smartpark_gate_cloud.py. "
        "Coloca este archivo en la raíz del proyecto, junto a "
        "smartpark_gate_cloud.py."
    ) from exc


# ============================================================
# SMARTPARK UCE - EDGE DEMO
# ============================================================

EDGE_HOST = "127.0.0.1"
EDGE_PORT = 9000

BACKEND_BASE_URL = os.getenv(
    "SMARTPARK_BACKEND_URL",
    "https://2uz85rgfg7.execute-api.us-east-1.amazonaws.com",
).rstrip("/")

SHOW_LOCAL_WINDOW = (
    os.getenv("SMARTPARK_SHOW_WINDOW", "true")
    .strip()
    .lower()
    in {"1", "true", "yes", "on"}
)

SIMULATED_DISTANCE_CM = float(
    os.getenv("SMARTPARK_DEMO_DISTANCE_CM", "12.0")
)

SIMULATED_TOPIC = os.getenv(
    "SMARTPARK_DEMO_TOPIC",
    "smartpark/gates/gate-01/detection",
)


# ============================================================
# ACTUALIZAR BACKEND DEL CORE EDGE
# ============================================================

gate.BACKEND_BASE_URL = BACKEND_BASE_URL

gate.HEALTH_URL = (
    f"{BACKEND_BASE_URL}/health"
)

gate.PROCESS_URL = (
    f"{BACKEND_BASE_URL}"
    "/api/v1/access/process"
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="SmartPark UCE Edge Demo Model Detection",
    version="1.4.0-demo",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://smartpark-uce-frontend-573672769830.s3-website-us-east-1.amazonaws.com",
        "https://production.d1kzks9pms1av2.amplifyapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# FRAME COMPARTIDO
# ============================================================

frame_lock = threading.Lock()
latest_frame = None


# ============================================================
# ESTADO COMPARTIDO
# ============================================================

state_lock = threading.Lock()

edge_state = {
    "stage": "WAITING",
    "state": "WAITING",
    "event_type": None,
    "sensor": "Esperando vehículo",
    "distance_cm": None,
    "track_id": None,
    "face_captured": False,
    "plate_captured": False,
    "decision": None,
    "person": None,
    "plate": None,
    "face_score": None,
    "plate_score": None,
    "reason": None,
    "barrier_state": "UNKNOWN",
    "processing": False,
    "message": "Esperando vehículo",
    "updated_at": time.time(),
    "demo_mode": True,
    "sensor_simulation_available": True,
    "compute_mode": DEVICE_INFO["mode"],
    "compute_device": COMPUTE_DEVICE,
}


def update_state(**values):
    with state_lock:
        for key, value in values.items():
            edge_state[key] = value

        edge_state["updated_at"] = time.time()


def get_state_copy():
    with state_lock:
        result = dict(edge_state)

    result["processing"] = bool(
        getattr(gate, "processing", False)
    )

    result["message"] = str(
        getattr(gate, "status_message", result["message"])
    )

    result["distance_cm"] = getattr(
        gate,
        "last_distance",
        result["distance_cm"],
    )

    mqtt_connection = getattr(
        gate,
        "mqtt_connection",
        None,
    )

    mqtt_connected = mqtt_connection is not None

    result["mqtt_connected"] = mqtt_connected

    if mqtt_connected:
        last_distance = getattr(
            gate,
            "last_distance",
            None,
        )

        if last_distance is not None:
            result["sensor"] = (
                f"Conectado · {last_distance} cm"
            )
        else:
            result["sensor"] = "Conectado"
    else:
        if result.get("sensor") != "SIMULADO · Vehículo detectado":
            result["sensor"] = "Esperando conexión / modo demo disponible"

    result["gate_id"] = "gate-01"
    result["backend_url"] = BACKEND_BASE_URL
    result["camera_ready"] = latest_frame is not None
    result["yolo"] = "YOLO11n"
    result["tracker"] = "ByteTrack"

    result["compute_mode"] = DEVICE_INFO["mode"]
    result["compute_device"] = COMPUTE_DEVICE
    result["cuda_available"] = DEVICE_INFO["cuda_available"]
    result["gpu_name"] = DEVICE_INFO["gpu_name"]
    result["gpu_memory_gb"] = DEVICE_INFO["gpu_memory_gb"]
    result["torch_version"] = DEVICE_INFO["torch_version"]
    result["torch_cuda_version"] = DEVICE_INFO["cuda_version"]
    result["ultralytics_device_patched"] = ULTRALYTICS_DEVICE_PATCHED
    result["demo_mode"] = True
    result["demo_trigger_key"] = "S"

    return result


# ============================================================
# INTERCEPTAR cv2.imshow
# ============================================================

original_imshow = cv2.imshow


def smartpark_imshow(window_name, frame):
    global latest_frame

    if (
        frame is not None
        and getattr(frame, "size", 0) > 0
    ):
        with frame_lock:
            latest_frame = frame.copy()

    if SHOW_LOCAL_WINDOW:
        original_imshow(
            window_name,
            frame,
        )


cv2.imshow = smartpark_imshow



# ============================================================
# CAPTURA REAL POR MODELOS - ROSTRO Y MATRÍCULA
# ============================================================
#
# IMPORTANTE:
#
# Esta versión NO intenta adivinar una placa por bordes/rectángulos.
#
# Rostro:
#   OpenCV YuNet -> detecta una CARA de verdad.
#
# Matrícula:
#   YOLOv8n especializado en license plates -> detecta una PLACA real.
#
# La barra de progreso:
#   - NO avanza si el modelo no detecta el objeto correcto.
#   - solo avanza con detecciones reales y suficientemente nítidas.
#
# Luego se envía el frame completo al Backend AWS como antes.
#
# Modelos pequeños:
#   YuNet ~0.2 MB
#   LP.pt ~6 MB
#
# Se descargan una sola vez y quedan guardados localmente.
# ============================================================


# ============================================================
# CONFIGURACIÓN DE MODELOS
# ============================================================

SMARTPARK_MODELS_DIR = Path(
    os.getenv(
        "SMARTPARK_LOCAL_MODELS_DIR",
        "models/smartpark",
    )
)

SMARTPARK_MODELS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


FACE_MODEL_PATH = SMARTPARK_MODELS_DIR / (
    "face_detection_yunet_2023mar.onnx"
)

PLATE_MODEL_PATH = SMARTPARK_MODELS_DIR / (
    "license_plate_yolov8n.pt"
)


FACE_MODEL_URLS = [
    (
        "https://media.githubusercontent.com/media/"
        "opencv/opencv_zoo/main/models/"
        "face_detection_yunet/"
        "face_detection_yunet_2023mar.onnx"
    ),
    (
        "https://github.com/opencv/opencv_zoo/raw/main/"
        "models/face_detection_yunet/"
        "face_detection_yunet_2023mar.onnx?download=1"
    ),
]

PLATE_MODEL_URLS = [
    (
        "https://raw.githubusercontent.com/"
        "LorenzoVenuti/license-plate-recognition/main/"
        "models/LP.pt"
    ),
]


FACE_MIN_CONFIDENCE = float(
    os.getenv(
        "SMARTPARK_FACE_DETECT_CONF",
        "0.88",
    )
)

FACE_MIN_SHARPNESS = float(
    os.getenv(
        "SMARTPARK_FACE_MIN_SHARPNESS",
        "42",
    )
)

FACE_REQUIRED_FRAMES = int(
    os.getenv(
        "SMARTPARK_FACE_GOOD_FRAMES",
        "3",
    )
)

FACE_WINDOW_SECONDS = float(
    os.getenv(
        "SMARTPARK_FACE_WINDOW",
        "1.25",
    )
)

FACE_TIMEOUT_SECONDS = float(
    os.getenv(
        "SMARTPARK_FACE_TIMEOUT",
        "15",
    )
)


PLATE_PREPARE_SECONDS = float(
    os.getenv(
        "SMARTPARK_PLATE_PREPARE_SECONDS",
        "4.0",
    )
)

PLATE_MIN_CONFIDENCE = float(
    os.getenv(
        "SMARTPARK_PLATE_DETECT_CONF",
        "0.55",
    )
)

PLATE_MIN_SHARPNESS = float(
    os.getenv(
        "SMARTPARK_PLATE_MIN_SHARPNESS",
        "32",
    )
)

PLATE_REQUIRED_FRAMES = int(
    os.getenv(
        "SMARTPARK_PLATE_GOOD_FRAMES",
        "3",
    )
)

PLATE_WINDOW_SECONDS = float(
    os.getenv(
        "SMARTPARK_PLATE_WINDOW",
        "1.35",
    )
)

PLATE_TIMEOUT_SECONDS = float(
    os.getenv(
        "SMARTPARK_PLATE_TIMEOUT",
        "20",
    )
)


# ============================================================
# DESCARGA SEGURA DE MODELOS
# ============================================================

def _download_model_if_needed(
    destination: Path,
    urls: list[str],
    minimum_bytes: int,
) -> bool:
    """
    Descarga un modelo una sola vez.

    Si ya existe con tamaño razonable, no vuelve a descargarlo.
    """
    try:
        if (
            destination.exists()
            and
            destination.stat().st_size >= minimum_bytes
        ):
            return True
    except OSError:
        pass

    print()
    print(
        f"[MODEL] Falta {destination.name}."
    )
    print(
        "[MODEL] Descargando una sola vez..."
    )

    temporary = destination.with_suffix(
        destination.suffix + ".part"
    )

    for url in urls:
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 SmartPark-UCE"
                    )
                },
            )

            with urllib.request.urlopen(
                request,
                timeout=45,
            ) as response:
                data = response.read()

            if len(data) < minimum_bytes:
                raise RuntimeError(
                    (
                        "archivo demasiado pequeño "
                        f"({len(data)} bytes)"
                    )
                )

            temporary.write_bytes(
                data
            )

            temporary.replace(
                destination
            )

            print(
                f"[MODEL] OK: {destination}"
            )

            return True

        except Exception as exc:
            print(
                f"[MODEL] Falló fuente: {exc}"
            )

    try:
        temporary.unlink(
            missing_ok=True
        )
    except Exception:
        pass

    print(
        f"[MODEL] No se pudo obtener "
        f"{destination.name}."
    )

    return False


# ============================================================
# CARGAR MODELO DE ROSTRO YUNET
# ============================================================

FACE_MODEL_READY = _download_model_if_needed(
    FACE_MODEL_PATH,
    FACE_MODEL_URLS,
    minimum_bytes=100_000,
)

FACE_DETECTOR = None

if FACE_MODEL_READY:
    try:
        if hasattr(
            cv2,
            "FaceDetectorYN_create",
        ):
            FACE_DETECTOR = (
                cv2.FaceDetectorYN_create(
                    str(FACE_MODEL_PATH),
                    "",
                    (320, 320),
                    FACE_MIN_CONFIDENCE,
                    0.3,
                    5000,
                )
            )
        else:
            FACE_DETECTOR = (
                cv2.FaceDetectorYN.create(
                    str(FACE_MODEL_PATH),
                    "",
                    (320, 320),
                    FACE_MIN_CONFIDENCE,
                    0.3,
                    5000,
                )
            )

        print(
            "[FACE] YuNet cargado correctamente ✅"
        )

    except Exception as exc:
        FACE_DETECTOR = None

        print(
            f"[FACE] No se pudo cargar YuNet: {exc}"
        )


# Fallback SOLO si YuNet no puede inicializarse.
# Sigue siendo un detector de rostros, no una heurística genérica.
HAAR_FACE_DETECTOR = cv2.CascadeClassifier(
    cv2.data.haarcascades
    +
    "haarcascade_frontalface_default.xml"
)


# ============================================================
# CARGAR MODELO YOLO ESPECIALIZADO EN MATRÍCULAS
# ============================================================

PLATE_MODEL_READY = _download_model_if_needed(
    PLATE_MODEL_PATH,
    PLATE_MODEL_URLS,
    minimum_bytes=1_000_000,
)

PLATE_DETECTOR = None

if PLATE_MODEL_READY:
    try:
        from ultralytics import YOLO

        PLATE_DETECTOR = YOLO(
            str(PLATE_MODEL_PATH)
        )

        print(
            "[PLATE] Detector YOLO de matrículas "
            "cargado correctamente ✅"
        )

    except Exception as exc:
        PLATE_DETECTOR = None

        print(
            f"[PLATE] No se pudo cargar "
            f"el detector: {exc}"
        )


# ============================================================
# UTILIDADES DE CALIDAD
# ============================================================

def _sharpness(image):
    if (
        image is None
        or
        image.size == 0
    ):
        return 0.0

    if len(image.shape) == 3:
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY,
        )
    else:
        gray = image

    return float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F,
        ).var()
    )


def _safe_crop(
    frame,
    x1,
    y1,
    x2,
    y2,
    pad_ratio=0.08,
):
    h, w = frame.shape[:2]

    bw = max(
        1,
        int(x2 - x1),
    )

    bh = max(
        1,
        int(y2 - y1),
    )

    px = int(
        bw * pad_ratio
    )

    py = int(
        bh * pad_ratio
    )

    xx1 = max(
        0,
        int(x1) - px,
    )

    yy1 = max(
        0,
        int(y1) - py,
    )

    xx2 = min(
        w,
        int(x2) + px,
    )

    yy2 = min(
        h,
        int(y2) + py,
    )

    crop = frame[
        yy1:yy2,
        xx1:xx2,
    ]

    return (
        crop,
        (
            xx1,
            yy1,
            xx2,
            yy2,
        ),
    )


def _bbox_iou(
    box_a,
    box_b,
):
    if (
        box_a is None
        or
        box_b is None
    ):
        return 0.0

    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    ix1 = max(
        ax1,
        bx1,
    )

    iy1 = max(
        ay1,
        by1,
    )

    ix2 = min(
        ax2,
        bx2,
    )

    iy2 = min(
        ay2,
        by2,
    )

    iw = max(
        0.0,
        ix2 - ix1,
    )

    ih = max(
        0.0,
        iy2 - iy1,
    )

    intersection = (
        iw * ih
    )

    area_a = max(
        0.0,
        ax2 - ax1,
    ) * max(
        0.0,
        ay2 - ay1,
    )

    area_b = max(
        0.0,
        bx2 - bx1,
    ) * max(
        0.0,
        by2 - by1,
    )

    union = (
        area_a
        +
        area_b
        -
        intersection
    )

    if union <= 0:
        return 0.0

    return float(
        intersection / union
    )


def _draw_progress(
    frame,
    label,
    valid_count,
    required_count,
    color,
    subtitle,
):
    progress = min(
        1.0,
        valid_count
        /
        max(
            1,
            required_count,
        ),
    )

    cv2.putText(
        frame,
        label,
        (30, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.78,
        color,
        2,
    )

    cv2.putText(
        frame,
        subtitle,
        (30, 78),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
    )

    cv2.rectangle(
        frame,
        (30, 95),
        (430, 115),
        (70, 70, 70),
        2,
    )

    # La barra SOLO crece a partir de frames
    # realmente detectados por el modelo.
    if valid_count > 0:
        cv2.rectangle(
            frame,
            (30, 95),
            (
                30
                +
                int(
                    400 * progress
                ),
                115,
            ),
            color,
            -1,
        )


# ============================================================
# DETECCIÓN REAL DE ROSTRO
# ============================================================

def _detect_face_model(
    frame,
):
    """
    Devuelve la mejor cara:
        bbox
        confidence

    YuNet primero.
    Haar solo como fallback si YuNet no está disponible.
    """
    h, w = frame.shape[:2]

    if FACE_DETECTOR is not None:
        try:
            FACE_DETECTOR.setInputSize(
                (w, h)
            )

            _, faces = (
                FACE_DETECTOR.detect(
                    frame
                )
            )

            if (
                faces is None
                or
                len(faces) == 0
            ):
                return None

            best = max(
                faces,
                key=lambda row: float(
                    row[-1]
                ),
            )

            confidence = float(
                best[-1]
            )

            if (
                confidence
                <
                FACE_MIN_CONFIDENCE
            ):
                return None

            x = int(
                best[0]
            )

            y = int(
                best[1]
            )

            bw = int(
                best[2]
            )

            bh = int(
                best[3]
            )

            return {
                "bbox": (
                    x,
                    y,
                    x + bw,
                    y + bh,
                ),
                "confidence": confidence,
                "source": "YuNet",
            }

        except Exception:
            pass

    # Fallback: Haar.
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY,
    )

    faces = (
        HAAR_FACE_DETECTOR
        .detectMultiScale(
            gray,
            scaleFactor=1.10,
            minNeighbors=6,
            minSize=(90, 90),
        )
    )

    if (
        faces is None
        or
        len(faces) == 0
    ):
        return None

    x, y, bw, bh = max(
        faces,
        key=lambda b: (
            int(b[2])
            *
            int(b[3])
        ),
    )

    return {
        "bbox": (
            int(x),
            int(y),
            int(x + bw),
            int(y + bh),
        ),
        "confidence": 1.0,
        "source": "Haar",
    }


def fast_capture_face(
    camera,
):
    print()
    print("=" * 72)
    print(
        "[FACE] DETECCIÓN REAL DE ROSTRO"
    )
    print(
        "[FACE] La barra SOLO avanza "
        "cuando YuNet detecta una cara."
    )
    print(
        "[FACE] Después se selecciona "
        "el frame facial más nítido."
    )

    start = time.time()

    recent_good = deque()

    best_frame = None
    best_score = float(
        "-inf"
    )

    last_console = 0.0
    last_bbox = None

    while (
        time.time() - start
        <
        FACE_TIMEOUT_SECONDS
    ):
        ok, frame = (
            camera.read()
        )

        if (
            not ok
            or
            frame is None
            or
            frame.size == 0
        ):
            time.sleep(
                0.02
            )
            continue

        now = time.time()

        detection = (
            _detect_face_model(
                frame
            )
        )

        # Quitar detecciones demasiado antiguas.
        while (
            recent_good
            and
            now - recent_good[0][0]
            >
            FACE_WINDOW_SECONDS
        ):
            recent_good.popleft()

        display = (
            frame.copy()
        )

        valid = False
        sharp = 0.0
        confidence = 0.0

        if detection is not None:
            bbox = detection[
                "bbox"
            ]

            confidence = float(
                detection[
                    "confidence"
                ]
            )

            x1, y1, x2, y2 = (
                bbox
            )

            crop, safe_bbox = (
                _safe_crop(
                    frame,
                    x1,
                    y1,
                    x2,
                    y2,
                    pad_ratio=0.10,
                )
            )

            sx1, sy1, sx2, sy2 = (
                safe_bbox
            )

            sharp = _sharpness(
                crop
            )

            face_width = (
                x2 - x1
            )

            face_height = (
                y2 - y1
            )

            size_ok = (
                face_width >= 90
                and
                face_height >= 90
            )

            # Si la cara salta totalmente de lugar,
            # iniciamos una nueva secuencia.
            if (
                last_bbox is not None
                and
                _bbox_iou(
                    bbox,
                    last_bbox,
                )
                <
                0.20
            ):
                recent_good.clear()

            last_bbox = bbox

            valid = (
                size_ok
                and
                sharp
                >=
                FACE_MIN_SHARPNESS
            )

            cv2.rectangle(
                display,
                (
                    int(x1),
                    int(y1),
                ),
                (
                    int(x2),
                    int(y2),
                ),
                (
                    0,
                    220,
                    0,
                )
                if valid
                else
                (
                    0,
                    190,
                    255,
                ),
                3,
            )

            if valid:
                score = (
                    confidence * 100.0
                    +
                    sharp
                )

                recent_good.append(
                    (
                        now,
                        score,
                        sharp,
                        confidence,
                        frame.copy(),
                        bbox,
                    )
                )

                if score > best_score:
                    best_score = (
                        score
                    )

                    best_frame = (
                        frame.copy()
                    )

        valid_count = len(
            recent_good
        )

        if detection is None:
            label = (
                "BUSCANDO ROSTRO REAL..."
            )

            subtitle = (
                "La barra no avanza "
                "hasta detectar una cara"
            )

            color = (
                0,
                190,
                255,
            )

        elif not valid:
            label = (
                "ROSTRO DETECTADO"
            )

            subtitle = (
                f"Ajusta enfoque | "
                f"Nitidez {sharp:.0f}"
            )

            color = (
                0,
                190,
                255,
            )

        else:
            label = (
                f"ROSTRO VALIDO "
                f"{valid_count}/"
                f"{FACE_REQUIRED_FRAMES}"
            )

            subtitle = (
                f"Confianza "
                f"{confidence:.0%} | "
                f"Nitidez {sharp:.0f}"
            )

            color = (
                0,
                220,
                0,
            )

        _draw_progress(
            display,
            label,
            valid_count,
            FACE_REQUIRED_FRAMES,
            color,
            subtitle,
        )

        cv2.imshow(
            "SmartPark UCE - Acceso",
            display,
        )

        cv2.waitKey(
            1
        )

        if (
            now - last_console
            >=
            0.45
        ):
            if detection is None:
                print(
                    "[FACE] No hay cara detectada. "
                    "Esperando..."
                )

            elif valid:
                print(
                    f"[FACE] Cara válida "
                    f"{valid_count}/"
                    f"{FACE_REQUIRED_FRAMES} "
                    f"| conf "
                    f"{confidence:.0%} "
                    f"| nitidez "
                    f"{sharp:.0f}"
                )

            else:
                print(
                    f"[FACE] Cara detectada, "
                    f"pero nitidez insuficiente "
                    f"({sharp:.0f})."
                )

            last_console = (
                now
            )

        if (
            valid_count
            >=
            FACE_REQUIRED_FRAMES
        ):
            selected = max(
                recent_good,
                key=lambda item: (
                    item[1]
                ),
            )

            print(
                "[FACE] Rostro confirmado ✅"
            )

            print(
                f"[FACE] Confianza detector: "
                f"{selected[3]:.0%}"
            )

            print(
                f"[FACE] Nitidez seleccionada: "
                f"{selected[2]:.0f}"
            )

            return selected[4]

        time.sleep(
            0.012
        )

    if best_frame is not None:
        print(
            "[FACE] Tiempo máximo alcanzado. "
            "No hubo suficientes frames consecutivos."
        )

    print(
        "[FACE] ❌ No se confirmó un rostro "
        "con calidad suficiente."
    )

    return None


# ============================================================
# PREPARACIÓN DE PLACA
# ============================================================

def _plate_prepare_countdown(
    camera,
):
    print()
    print(
        f"[PLATE] Tienes "
        f"{PLATE_PREPARE_SECONDS:.0f}s "
        "para apuntar la cámara a la placa."
    )

    start = time.time()
    last_number = None

    while True:
        elapsed = (
            time.time()
            -
            start
        )

        remaining = (
            PLATE_PREPARE_SECONDS
            -
            elapsed
        )

        if remaining <= 0:
            return

        ok, frame = (
            camera.read()
        )

        if (
            not ok
            or
            frame is None
            or
            frame.size == 0
        ):
            time.sleep(
                0.02
            )
            continue

        display = (
            frame.copy()
        )

        cv2.putText(
            display,
            "PREPARA LA MATRICULA",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.95,
            (0, 220, 255),
            3,
        )

        cv2.putText(
            display,
            (
                f"Deteccion inicia en "
                f"{remaining:.1f}s"
            ),
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (255, 255, 255),
            2,
        )

        cv2.imshow(
            "SmartPark UCE - Acceso",
            display,
        )

        cv2.waitKey(
            1
        )

        number = max(
            1,
            int(
                np.ceil(
                    remaining
                )
            ),
        )

        if (
            number
            !=
            last_number
        ):
            print(
                f"[PLATE] Prepárala: "
                f"{number}..."
            )

            last_number = (
                number
            )

        time.sleep(
            0.015
        )


# ============================================================
# DETECCIÓN REAL DE MATRÍCULA CON YOLO
# ============================================================

def _detect_plate_model(
    frame,
):
    """
    Devuelve la mejor matrícula detectada por el
    MODELO YOLO especializado.

    No se usan contornos ni cajas geométricas inventadas.
    """
    if PLATE_DETECTOR is None:
        return None

    results = PLATE_DETECTOR.predict(
        source=frame,
        conf=PLATE_MIN_CONFIDENCE,
        imgsz=640,
        device=COMPUTE_DEVICE,
        verbose=False,
    )

    if (
        not results
        or
        results[0].boxes is None
        or
        len(results[0].boxes) == 0
    ):
        return None

    best = None
    best_conf = -1.0

    for box in results[0].boxes:
        confidence = float(
            box.conf[0].item()
        )

        coords = (
            box.xyxy[0]
            .detach()
            .cpu()
            .tolist()
        )

        x1, y1, x2, y2 = [
            int(v)
            for v in coords
        ]

        width = (
            x2 - x1
        )

        height = (
            y2 - y1
        )

        if (
            width < 70
            or
            height < 18
        ):
            continue

        if confidence > best_conf:
            best_conf = (
                confidence
            )

            best = {
                "bbox": (
                    x1,
                    y1,
                    x2,
                    y2,
                ),
                "confidence": (
                    confidence
                ),
            }

    return best


def fast_capture_plate(
    camera,
):
    print()
    print("=" * 72)
    print(
        "[PLATE] DETECCIÓN REAL DE MATRÍCULA"
    )

    if PLATE_DETECTOR is None:
        print(
            "[PLATE] ❌ El modelo especializado "
            "de placa no está disponible."
        )

        print(
            f"[PLATE] Archivo esperado: "
            f"{PLATE_MODEL_PATH}"
        )

        return None

    # Primero el usuario mueve la cámara.
    # Durante esta fase NO se analiza la placa.
    _plate_prepare_countdown(
        camera
    )

    print(
        "[PLATE] Detector YOLO activo."
    )

    print(
        "[PLATE] La barra SOLO avanzará "
        "si el modelo encuentra una matrícula."
    )

    start = time.time()

    recent_good = deque()

    best_frame = None
    best_score = float(
        "-inf"
    )

    last_bbox = None
    last_console = 0.0

    while (
        time.time() - start
        <
        PLATE_TIMEOUT_SECONDS
    ):
        ok, frame = (
            camera.read()
        )

        if (
            not ok
            or
            frame is None
            or
            frame.size == 0
        ):
            time.sleep(
                0.02
            )
            continue

        now = time.time()

        detection = (
            _detect_plate_model(
                frame
            )
        )

        while (
            recent_good
            and
            now - recent_good[0][0]
            >
            PLATE_WINDOW_SECONDS
        ):
            recent_good.popleft()

        display = (
            frame.copy()
        )

        valid = False
        sharp = 0.0
        confidence = 0.0

        if detection is not None:
            bbox = detection[
                "bbox"
            ]

            confidence = float(
                detection[
                    "confidence"
                ]
            )

            x1, y1, x2, y2 = (
                bbox
            )

            crop, _ = (
                _safe_crop(
                    frame,
                    x1,
                    y1,
                    x2,
                    y2,
                    pad_ratio=0.08,
                )
            )

            sharp = _sharpness(
                crop
            )

            # Si el bbox cambia totalmente de lugar,
            # no mezclamos detecciones diferentes.
            if (
                last_bbox is not None
                and
                _bbox_iou(
                    bbox,
                    last_bbox,
                )
                <
                0.25
            ):
                recent_good.clear()

            last_bbox = (
                bbox
            )

            valid = (
                sharp
                >=
                PLATE_MIN_SHARPNESS
            )

            cv2.rectangle(
                display,
                (
                    int(x1),
                    int(y1),
                ),
                (
                    int(x2),
                    int(y2),
                ),
                (
                    0,
                    220,
                    0,
                )
                if valid
                else
                (
                    0,
                    190,
                    255,
                ),
                3,
            )

            if valid:
                score = (
                    confidence * 180.0
                    +
                    sharp
                )

                recent_good.append(
                    (
                        now,
                        score,
                        sharp,
                        confidence,
                        frame.copy(),
                        bbox,
                    )
                )

                if score > best_score:
                    best_score = (
                        score
                    )

                    best_frame = (
                        frame.copy()
                    )

        valid_count = len(
            recent_good
        )

        if detection is None:
            label = (
                "BUSCANDO MATRICULA REAL..."
            )

            subtitle = (
                "Sin placa detectada "
                "- barra detenida"
            )

            color = (
                0,
                190,
                255,
            )

        elif not valid:
            label = (
                "MATRICULA DETECTADA"
            )

            subtitle = (
                f"Conf "
                f"{confidence:.0%} | "
                f"enfoca mejor "
                f"({sharp:.0f})"
            )

            color = (
                0,
                190,
                255,
            )

        else:
            label = (
                f"MATRICULA VALIDA "
                f"{valid_count}/"
                f"{PLATE_REQUIRED_FRAMES}"
            )

            subtitle = (
                f"Confianza "
                f"{confidence:.0%} | "
                f"Nitidez {sharp:.0f}"
            )

            color = (
                0,
                220,
                0,
            )

        _draw_progress(
            display,
            label,
            valid_count,
            PLATE_REQUIRED_FRAMES,
            color,
            subtitle,
        )

        cv2.imshow(
            "SmartPark UCE - Acceso",
            display,
        )

        cv2.waitKey(
            1
        )

        if (
            now - last_console
            >=
            0.45
        ):
            if detection is None:
                print(
                    "[PLATE] No hay matrícula "
                    "detectada. Esperando..."
                )

            elif valid:
                print(
                    f"[PLATE] Matrícula real "
                    f"{valid_count}/"
                    f"{PLATE_REQUIRED_FRAMES} "
                    f"| conf "
                    f"{confidence:.0%} "
                    f"| nitidez "
                    f"{sharp:.0f}"
                )

            else:
                print(
                    f"[PLATE] Matrícula detectada "
                    f"pero desenfocada "
                    f"({sharp:.0f})."
                )

            last_console = (
                now
            )

        if (
            valid_count
            >=
            PLATE_REQUIRED_FRAMES
        ):
            selected = max(
                recent_good,
                key=lambda item: (
                    item[1]
                ),
            )

            print(
                "[PLATE] Matrícula confirmada ✅"
            )

            print(
                f"[PLATE] Confianza detector: "
                f"{selected[3]:.0%}"
            )

            print(
                f"[PLATE] Nitidez seleccionada: "
                f"{selected[2]:.0f}"
            )

            print(
                "[PLATE] Se enviará el FRAME COMPLETO "
                "al PaddleOCR AWS."
            )

            return selected[4]

        time.sleep(
            0.012
        )

    print()
    print(
        "[PLATE] ❌ No se confirmó una matrícula real."
    )

    print(
        "[PLATE] No se enviará una imagen falsa "
        "al OCR."
    )

    return None



# Reemplazamos SOLO la captura local.
# Tracking, AWS, RDS, IoT y autorización permanecen iguales.
gate.capture_face = fast_capture_face
gate.capture_plate = fast_capture_plate



# ============================================================
# FUNCIONES ORIGINALES DEL CORE
# ============================================================

original_on_mqtt_message = gate.on_mqtt_message
original_realtime_tracking = gate.realtime_vehicle_tracking
original_capture_face = gate.capture_face
original_capture_plate = gate.capture_plate
original_process_access = gate.process_access
original_automatic_cycle = gate.automatic_access_cycle


# ============================================================
# WRAPPER MQTT / SENSOR
# ============================================================

def edge_on_mqtt_message(
    topic,
    payload,
    dup,
    qos,
    retain,
    **kwargs,
):
    try:
        message = json.loads(
            payload.decode("utf-8")
        )

        event = message.get("event")
        distance = message.get("distance_cm")

        if event == "VEHICLE_DETECTED":
            update_state(
                stage="VEHICLE_DETECTED",
                state="VEHICLE_DETECTED",
                sensor="Vehículo detectado",
                distance_cm=distance,
                event_type=None,
                face_captured=False,
                plate_captured=False,
                decision=None,
                person=None,
                plate=None,
                face_score=None,
                plate_score=None,
                reason=None,
                message="Vehículo detectado",
            )

    except Exception:
        pass

    return original_on_mqtt_message(
        topic,
        payload,
        dup,
        qos,
        retain,
        **kwargs,
    )


# ============================================================
# WRAPPER TRACKING
# ============================================================

def edge_realtime_tracking(camera):
    update_state(
        stage="TRACKING",
        state="TRACKING",
        processing=True,
        message=(
            "YOLO11n + ByteTrack activos "
            f"({DEVICE_INFO['mode']} / {COMPUTE_DEVICE})"
        ),
    )

    event_type = original_realtime_tracking(
        camera
    )

    if event_type:
        update_state(
            stage="CROSSING",
            state="CROSSING",
            event_type=event_type,
            message=f"Movimiento detectado: {event_type}",
        )
    else:
        update_state(
            stage="WAITING",
            state="WAITING",
            event_type=None,
            message="No se detectó cruce",
        )

    return event_type


# ============================================================
# WRAPPER ROSTRO
# ============================================================

def edge_capture_face(camera):
    update_state(
        stage="FACE",
        state="FACE",
        face_captured=False,
        message="Buscando rostro",
    )

    frame = original_capture_face(
        camera
    )

    if frame is not None:
        update_state(
            face_captured=True,
            message="Rostro capturado",
        )
    else:
        update_state(
            face_captured=False,
            message="No se obtuvo rostro",
        )

    return frame


# ============================================================
# WRAPPER PLACA
# ============================================================

def edge_capture_plate(camera):
    update_state(
        stage="PLATE",
        state="PLATE",
        plate_captured=False,
        message="Buscando placa",
    )

    frame = original_capture_plate(
        camera
    )

    if frame is not None:
        update_state(
            plate_captured=True,
            message="Placa capturada",
        )
    else:
        update_state(
            plate_captured=False,
            message="No se obtuvo placa",
        )

    return frame


# ============================================================
# WRAPPER PROCESAMIENTO AWS
# ============================================================

def edge_process_access(
    face_frame,
    plate_frame,
    event_type,
):
    update_state(
        stage="PROCESSING",
        state="PROCESSING",
        event_type=event_type,
        message="Procesando en AWS",
    )

    result = original_process_access(
        face_frame,
        plate_frame,
        event_type,
    )

    if result is None:
        update_state(
            stage="RESULT",
            state="RESULT",
            decision="ERROR",
            message="Error procesando acceso",
        )
        return None

    decision = result.get("decision")
    person = result.get("person")
    plate = result.get("plate")
    face_score = result.get("face_score")
    plate_score = result.get("plate_score")
    reason = result.get("reason")

    update_state(
        stage="RESULT",
        state="RESULT",
        event_type=event_type,
        decision=decision,
        person=person,
        plate=plate,
        face_score=face_score,
        plate_score=plate_score,
        reason=reason,
        message=str(
            decision
            or "Resultado recibido"
        ),
    )

    return result


# ============================================================
# WRAPPER CICLO AUTOMÁTICO
# ============================================================

def edge_automatic_cycle(camera):
    update_state(
        processing=True,
        face_captured=False,
        plate_captured=False,
    )

    try:
        return original_automatic_cycle(
            camera
        )
    finally:
        update_state(
            stage="WAITING",
            state="WAITING",
            processing=False,
            event_type=None,
            message="Esperando siguiente vehículo",
        )


# ============================================================
# ACTIVAR WRAPPERS
# ============================================================

gate.on_mqtt_message = edge_on_mqtt_message
gate.realtime_vehicle_tracking = edge_realtime_tracking
gate.capture_face = edge_capture_face
gate.capture_plate = edge_capture_plate
gate.process_access = edge_process_access
gate.automatic_access_cycle = edge_automatic_cycle


# ============================================================
# SIMULADOR DE SENSOR HC-SR04
# ============================================================

simulation_lock = threading.Lock()
last_simulation_at = 0.0


def simulate_vehicle_detected(
    distance_cm: float | None = None,
) -> dict[str, Any]:
    """
    Simula exactamente el evento MQTT de detección del sensor.

    El resto del flujo sigue siendo REAL:
      YOLO -> ByteTrack -> rostro -> placa -> AWS -> autorización -> IoT
    """
    global last_simulation_at

    if distance_cm is None:
        distance_cm = SIMULATED_DISTANCE_CM

    with simulation_lock:
        now = time.time()

        # Evita dobles pulsaciones accidentales.
        if now - last_simulation_at < 1.0:
            return {
                "ok": False,
                "reason": "debounce",
                "message": "Espera un segundo antes de volver a simular.",
            }

        if bool(getattr(gate, "processing", False)):
            return {
                "ok": False,
                "reason": "busy",
                "message": "SmartPark ya está procesando un vehículo.",
            }

        last_simulation_at = now

        payload = json.dumps(
            {
                "event": "VEHICLE_DETECTED",
                "distance_cm": float(distance_cm),
                "source": "DEMO_KEYBOARD",
            }
        ).encode("utf-8")

        update_state(
            stage="VEHICLE_DETECTED",
            state="VEHICLE_DETECTED",
            sensor="SIMULADO · Vehículo detectado",
            distance_cm=float(distance_cm),
            message="Evento HC-SR04 simulado",
        )

        print()
        print("=" * 72)
        print("[DEMO] SENSOR SIMULADO")
        print(
            f"[DEMO] VEHICLE_DETECTED · "
            f"{float(distance_cm):.1f} cm"
        )
        print(
            "[DEMO] A partir de aquí el flujo continúa "
            "con la lógica REAL de SmartPark."
        )
        print("=" * 72)
        print()

        # Invoca el mismo callback usado por el mensaje MQTT real.
        gate.on_mqtt_message(
            SIMULATED_TOPIC,
            payload,
            False,
            0,
            False,
        )

        return {
            "ok": True,
            "event": "VEHICLE_DETECTED",
            "distance_cm": float(distance_cm),
            "topic": SIMULATED_TOPIC,
        }


def _print_demo_help():
    print()
    print("-" * 72)
    print("CONTROLES DE DEMOSTRACIÓN")
    print("-" * 72)
    print("  S  -> Simular HC-SR04 / VEHICLE_DETECTED")
    print("  D  -> Mostrar CPU/GPU seleccionado")
    print("  H  -> Mostrar esta ayuda")
    print("  Ctrl+C -> Detener SmartPark")
    print("-" * 72)
    print()


def _print_device_info():
    print()
    print("-" * 72)
    print("DISPOSITIVO DE PROCESAMIENTO")
    print("-" * 72)
    print(
        f"Solicitado : {DEVICE_INFO['requested'].upper()}"
    )
    print(
        f"Modo real  : {DEVICE_INFO['mode']}"
    )
    print(
        f"Device     : {COMPUTE_DEVICE}"
    )
    print(
        f"CUDA       : {DEVICE_INFO['cuda_available']}"
    )
    print(
        f"GPU        : {DEVICE_INFO['gpu_name'] or 'No disponible'}"
    )
    print(
        f"VRAM       : "
        f"{DEVICE_INFO['gpu_memory_gb'] or '—'} GB"
    )
    print(
        f"PyTorch    : {DEVICE_INFO['torch_version']}"
    )
    print(
        f"Torch CUDA : {DEVICE_INFO['cuda_version'] or '—'}"
    )
    print(
        f"YOLO patch : {ULTRALYTICS_DEVICE_PATCHED}"
    )
    if DEVICE_INFO["fallback"]:
        print(
            "AVISO      : Se solicitó GPU, pero CUDA no está "
            "disponible. Se usará CPU."
        )
    print("-" * 72)
    print()


def keyboard_demo_loop():
    """
    Lee teclas sin bloquear el hilo principal.

    Windows:
        usa msvcrt y responde al instante.

    Linux/macOS:
        permite escribir S + ENTER.
    """
    _print_demo_help()

    if os.name == "nt":
        import msvcrt

        while True:
            try:
                if msvcrt.kbhit():
                    raw = msvcrt.getwch()
                    key = raw.lower()

                    if key == "s":
                        simulate_vehicle_detected()
                    elif key == "d":
                        _print_device_info()
                    elif key == "h":
                        _print_demo_help()

                time.sleep(0.08)

            except Exception as exc:
                print(
                    f"[DEMO] Error leyendo teclado: {exc}"
                )
                time.sleep(0.5)

    else:
        while True:
            try:
                value = input().strip().lower()

                if value == "s":
                    simulate_vehicle_detected()
                elif value == "d":
                    _print_device_info()
                elif value == "h":
                    _print_demo_help()

            except Exception:
                time.sleep(0.5)


# ============================================================
# PLACEHOLDER VIDEO
# ============================================================

def create_placeholder_frame():
    width = 1280
    height = 720

    frame = np.zeros(
        (
            height,
            width,
            3,
        ),
        dtype=np.uint8,
    )

    frame[:] = (
        7,
        13,
        23,
    )

    cv2.putText(
        frame,
        "SMARTPARK UCE - EDGE DEMO",
        (50, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.1,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        "Esperando camara Edge...",
        (50, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (120, 150, 180),
        2,
    )

    cv2.putText(
        frame,
        f"Procesamiento: {DEVICE_INFO['mode']} ({COMPUTE_DEVICE})",
        (50, 205),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (120, 150, 180),
        2,
    )

    cv2.putText(
        frame,
        "Tecla S = simular HC-SR04",
        (50, 260),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (120, 150, 180),
        2,
    )

    return frame


# ============================================================
# GENERADOR MJPEG
# ============================================================

def video_generator():
    while True:
        with frame_lock:
            if latest_frame is None:
                frame = create_placeholder_frame()
            else:
                frame = latest_frame.copy()

        success, encoded = cv2.imencode(
            ".jpg",
            frame,
            [
                int(cv2.IMWRITE_JPEG_QUALITY),
                82,
            ],
        )

        if not success:
            time.sleep(0.05)
            continue

        jpeg = encoded.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpeg
            + b"\r\n"
        )

        time.sleep(0.05)


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "service": "SmartPark UCE Edge Demo",
        "gate": "gate-01",
        "version": "1.4.0-demo",
        "health": "/health",
        "status": "/status",
        "video": "/video",
        "device": "/demo/device",
        "simulate_sensor": "POST /demo/trigger",
        "demo_key": "S",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "smartpark-edge-demo",
        "version": "1.4.0-demo",
        "gate_id": "gate-01",
        "backend": BACKEND_BASE_URL,
        "camera_ready": latest_frame is not None,
        "mqtt_connected": (
            getattr(gate, "mqtt_connection", None)
            is not None
        ),
        "yolo": "YOLO11n",
        "tracker": "ByteTrack",
        "demo_mode": True,
        "demo_trigger_key": "S",
        "compute_mode": DEVICE_INFO["mode"],
        "compute_device": COMPUTE_DEVICE,
        "cuda_available": DEVICE_INFO["cuda_available"],
        "gpu_name": DEVICE_INFO["gpu_name"],
        "gpu_memory_gb": DEVICE_INFO["gpu_memory_gb"],
        "torch_version": DEVICE_INFO["torch_version"],
        "torch_cuda_version": DEVICE_INFO["cuda_version"],
        "ultralytics_device_patched": ULTRALYTICS_DEVICE_PATCHED,
    }


@app.get("/status")
def status():
    return get_state_copy()


@app.get("/video")
def video():
    return StreamingResponse(
        video_generator(),
        media_type=(
            "multipart/"
            "x-mixed-replace;"
            "boundary=frame"
        ),
    )


@app.get("/demo/device")
def demo_device():
    return {
        **DEVICE_INFO,
        "compute_device": COMPUTE_DEVICE,
        "ultralytics_device_patched": ULTRALYTICS_DEVICE_PATCHED,
        "platform": platform.platform(),
        "python": sys.version,
    }


@app.post("/demo/trigger")
def demo_trigger(
    distance_cm: float = SIMULATED_DISTANCE_CM,
):
    if not (1.0 <= distance_cm <= 400.0):
        raise HTTPException(
            status_code=422,
            detail="distance_cm debe estar entre 1 y 400 cm",
        )

    return simulate_vehicle_detected(
        distance_cm
    )


# ============================================================
# SERVIDOR FASTAPI
# ============================================================

def run_api_server():
    config = uvicorn.Config(
        app,
        host=EDGE_HOST,
        port=EDGE_PORT,
        log_level="warning",
        access_log=False,
    )

    server = uvicorn.Server(
        config
    )

    server.run()


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print("=" * 72)
    print("SMARTPARK UCE")
    print("EDGE DEMO · CPU/GPU + SENSOR SIMULADO")
    print("=" * 72)
    print()

    print(
        f"[EDGE] Backend AWS: {BACKEND_BASE_URL}"
    )
    print(
        f"[EDGE] API local: http://{EDGE_HOST}:{EDGE_PORT}"
    )
    print(
        f"[EDGE] Health: http://{EDGE_HOST}:{EDGE_PORT}/health"
    )
    print(
        f"[EDGE] Status: http://{EDGE_HOST}:{EDGE_PORT}/status"
    )
    print(
        f"[EDGE] Video: http://{EDGE_HOST}:{EDGE_PORT}/video"
    )
    print(
        f"[EDGE] Demo trigger: POST "
        f"http://{EDGE_HOST}:{EDGE_PORT}/demo/trigger"
    )

    _print_device_info()

    if DEVICE_INFO["fallback"]:
        print(
            "[DEVICE] Se pidió GPU, pero PyTorch no tiene CUDA "
            "disponible. SmartPark continuará en CPU."
        )

    # API local.
    api_thread = threading.Thread(
        target=run_api_server,
        daemon=True,
    )
    api_thread.start()

    # Teclado de demo.
    keyboard_thread = threading.Thread(
        target=keyboard_demo_loop,
        daemon=True,
    )
    keyboard_thread.start()

    time.sleep(1.2)

    print(
        "[DEMO] Presiona S en esta terminal para simular "
        "la detección del HC-SR04."
    )
    print(
        "[DEMO] Después de la simulación, el flujo hacia AWS "
        "continúa sin cambios."
    )
    print()

    try:
        # Mantener el core original en el hilo principal.
        gate.main()

    except KeyboardInterrupt:
        print()
        print("[EDGE] Sistema detenido.")


if __name__ == "__main__":
    main()
