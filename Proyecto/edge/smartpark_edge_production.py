"""
SmartPark UCE - Edge Production Launcher v1.0
=============================================

Este archivo convierte la versión V3 ya probada en un runtime de PRODUCCIÓN:

- Sensor REAL HC-SR04 por AWS IoT/MQTT.
- NO inicia la tecla S ni el simulador.
- AUTO / CPU / GPU mediante configuración.
- Puede detectar automáticamente la cámara.
- Mantiene:
    YOLO11n + ByteTrack
    YuNet para presencia de rostro
    YOLO especializado para presencia de matrícula
    API Gateway
    Backend AWS
    IA / OCR / RDS / AWS IoT
    API local 127.0.0.1:9000

IMPORTANTE:
Debe estar junto a:
    edge_server_demo_gpu_model_detection_v3.py
    smartpark_gate_cloud.py
    yolo11n.pt
    certs/

Más adelante este conjunto se empaquetará como SmartParkEdgeSetup.exe.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import threading
import time


APP_NAME = "SmartPark UCE Edge"
APP_VERSION = "1.0.0"

DEFAULT_BACKEND_URL = (
    "https://2uz85rgfg7.execute-api.us-east-1.amazonaws.com"
)


# ============================================================
# RUTAS
# ============================================================

def _runtime_dir() -> Path:
    """
    Carpeta donde vive el ejecutable o script.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


RUNTIME_DIR = _runtime_dir()

CONFIG_PATH = RUNTIME_DIR / "smartpark_edge_config.json"


# ============================================================
# CONFIG
# ============================================================

DEFAULT_CONFIG = {
    "gate_id": "gate-01",

    # "auto" busca una cámara disponible.
    # También puede ser 0, 1, 2...
    "camera_source": "auto",

    # auto | cpu | cuda
    "device": "auto",

    # PRODUCCIÓN = real.
    # El simulador NO se inicia en este launcher.
    "sensor_mode": "real",

    "show_local_window": True,

    "backend_url": DEFAULT_BACKEND_URL,

    "edge_host": "127.0.0.1",
    "edge_port": 9000,

    "camera_width": 1280,
    "camera_height": 720,

    "iot": {
        "client_id": "smartpark-camera-gate-01",
        "detection_topic": (
            "smartpark/gates/gate-01/detection"
        ),
        "root_ca": (
            "certs/camera/AmazonRootCA1.pem"
        ),
        "certificate": (
            "certs/camera/camera-certificate.pem.crt"
        ),
        "private_key": (
            "certs/camera/camera-private.pem.key"
        ),
    },
}


def _deep_merge(base, custom):
    result = dict(base)

    for key, value in custom.items():
        if (
            key in result
            and
            isinstance(result[key], dict)
            and
            isinstance(value, dict)
        ):
            result[key] = _deep_merge(
                result[key],
                value,
            )
        else:
            result[key] = value

    return result


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps(
                DEFAULT_CONFIG,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print(
            f"[CONFIG] Creado: {CONFIG_PATH}"
        )

        return dict(DEFAULT_CONFIG)

    try:
        custom = json.loads(
            CONFIG_PATH.read_text(
                encoding="utf-8"
            )
        )
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo leer {CONFIG_PATH}: {exc}"
        ) from exc

    return _deep_merge(
        DEFAULT_CONFIG,
        custom,
    )


CONFIG = load_config()


# ============================================================
# VALIDACIÓN CONFIG
# ============================================================

device_mode = str(
    CONFIG.get(
        "device",
        "auto",
    )
).strip().lower()

if device_mode not in {
    "auto",
    "cpu",
    "cuda",
}:
    device_mode = "auto"


sensor_mode = str(
    CONFIG.get(
        "sensor_mode",
        "real",
    )
).strip().lower()

if sensor_mode != "real":
    print(
        "[CONFIG] sensor_mode no es 'real'. "
        "Este launcher de producción lo forzará a REAL."
    )

sensor_mode = "real"


backend_url = str(
    CONFIG.get(
        "backend_url",
        DEFAULT_BACKEND_URL,
    )
).rstrip("/")


gate_id = str(
    CONFIG.get(
        "gate_id",
        "gate-01",
    )
).strip()

if not gate_id:
    gate_id = "gate-01"


# ============================================================
# VARIABLES ANTES DE IMPORTAR V3
# ============================================================

os.environ["SMARTPARK_DEVICE"] = device_mode

os.environ["SMARTPARK_BACKEND_URL"] = (
    backend_url
)

os.environ["SMARTPARK_SHOW_WINDOW"] = (
    "true"
    if bool(
        CONFIG.get(
            "show_local_window",
            True,
        )
    )
    else
    "false"
)


# Evitamos que la V3 muestre el menú interactivo.
# Toda selección viene del JSON.
sys.argv = [
    sys.argv[0],
    "--no-menu",
]


# ============================================================
# IMPORTAR MOTOR V3 YA PROBADO
# ============================================================

try:
    import edge_server_demo_gpu_model_detection_v3 as edge
except Exception as exc:
    raise RuntimeError(
        "No se pudo cargar "
        "edge_server_demo_gpu_model_detection_v3.py.\n"
        "Ponlo en la misma carpeta que "
        "smartpark_edge_production.py."
    ) from exc


# ============================================================
# UTILIDADES
# ============================================================

def _absolute_resource(
    relative_or_absolute: str,
) -> str:
    path = Path(
        relative_or_absolute
    )

    if path.is_absolute():
        return str(path)

    return str(
        (
            RUNTIME_DIR
            /
            path
        ).resolve()
    )


def detect_camera_source(
    max_index: int = 6,
) -> int:
    """
    Busca una cámara que realmente entregue frames.

    Esto evita depender siempre de CAMERA_SOURCE = 0.
    """
    import cv2

    print(
        "[CAMERA] Buscando cámara disponible..."
    )

    for index in range(
        max_index
    ):
        camera = None

        try:
            # En Windows CAP_DSHOW suele evitar
            # esperas largas al abrir cámaras.
            if os.name == "nt":
                camera = cv2.VideoCapture(
                    index,
                    cv2.CAP_DSHOW,
                )
            else:
                camera = cv2.VideoCapture(
                    index
                )

            if not camera.isOpened():
                continue

            camera.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                int(
                    CONFIG.get(
                        "camera_width",
                        1280,
                    )
                ),
            )

            camera.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                int(
                    CONFIG.get(
                        "camera_height",
                        720,
                    )
                ),
            )

            # Dar un pequeño tiempo de inicialización.
            time.sleep(
                0.15
            )

            ok, frame = (
                camera.read()
            )

            if (
                ok
                and
                frame is not None
                and
                getattr(
                    frame,
                    "size",
                    0,
                )
                > 0
            ):
                print(
                    f"[CAMERA] Detectada en índice {index} ✅"
                )

                return index

        except Exception:
            pass

        finally:
            try:
                if camera is not None:
                    camera.release()
            except Exception:
                pass

    raise RuntimeError(
        "No se encontró ninguna cámara disponible. "
        "Conecta DroidCam/USB y vuelve a iniciar SmartPark Edge."
    )


# ============================================================
# APLICAR CONFIGURACIÓN AL CORE REAL
# ============================================================

def configure_core() -> int:
    camera_source = CONFIG.get(
        "camera_source",
        "auto",
    )

    if (
        isinstance(
            camera_source,
            str,
        )
        and
        camera_source.strip().lower()
        == "auto"
    ):
        camera_index = (
            detect_camera_source()
        )
    else:
        try:
            camera_index = int(
                camera_source
            )
        except Exception as exc:
            raise RuntimeError(
                "camera_source debe ser "
                "'auto' o un número entero."
            ) from exc

    # Cámara real.
    edge.gate.CAMERA_SOURCE = (
        camera_index
    )

    edge.gate.CAMERA_WIDTH = int(
        CONFIG.get(
            "camera_width",
            1280,
        )
    )

    edge.gate.CAMERA_HEIGHT = int(
        CONFIG.get(
            "camera_height",
            720,
        )
    )

    # Backend estable.
    edge.gate.BACKEND_BASE_URL = (
        backend_url
    )

    edge.gate.HEALTH_URL = (
        f"{backend_url}/health"
    )

    edge.gate.PROCESS_URL = (
        f"{backend_url}"
        "/api/v1/access/process"
    )

    edge.BACKEND_BASE_URL = (
        backend_url
    )

    # IoT real.
    iot = CONFIG.get(
        "iot",
        {},
    )

    detection_topic = str(
        iot.get(
            "detection_topic",
            (
                f"smartpark/gates/"
                f"{gate_id}/detection"
            ),
        )
    )

    client_id = str(
        iot.get(
            "client_id",
            (
                "smartpark-camera-"
                f"{gate_id}"
            ),
        )
    )

    edge.gate.TOPIC_DETECTION = (
        detection_topic
    )

    edge.gate.MQTT_CLIENT_ID = (
        client_id
    )

    edge.gate.ROOT_CA = (
        _absolute_resource(
            str(
                iot.get(
                    "root_ca",
                    (
                        "certs/camera/"
                        "AmazonRootCA1.pem"
                    ),
                )
            )
        )
    )

    edge.gate.CERTIFICATE = (
        _absolute_resource(
            str(
                iot.get(
                    "certificate",
                    (
                        "certs/camera/"
                        "camera-certificate.pem.crt"
                    ),
                )
            )
        )
    )

    edge.gate.PRIVATE_KEY = (
        _absolute_resource(
            str(
                iot.get(
                    "private_key",
                    (
                        "certs/camera/"
                        "camera-private.pem.key"
                    ),
                )
            )
        )
    )

    # La UI local sigue usando gate-01 hoy.
    # Dejamos el dato correcto disponible en estado.
    try:
        edge.edge_state[
            "gate_id"
        ] = gate_id

        edge.edge_state[
            "sensor"
        ] = (
            "Esperando HC-SR04 real"
        )

        edge.edge_state[
            "demo_mode"
        ] = False

        edge.edge_state[
            "sensor_simulation_available"
        ] = False

    except Exception:
        pass

    return camera_index


# ============================================================
# DESACTIVAR SIMULADOR HTTP DE V3
# ============================================================

def disable_demo_routes():
    """
    Elimina del FastAPI local las rutas de simulación
    para esta versión de producción.
    """
    demo_paths = {
        "/demo/trigger",
    }

    edge.app.router.routes = [
        route
        for route
        in edge.app.router.routes
        if getattr(
            route,
            "path",
            None,
        )
        not in demo_paths
    ]


# ============================================================
# STARTUP
# ============================================================

def print_startup(
    camera_index: int,
):
    print()
    print("=" * 72)
    print(
        f"{APP_NAME} v{APP_VERSION}"
    )
    print(
        "MODO PRODUCCIÓN"
    )
    print("=" * 72)
    print(
        f"Garita       : {gate_id}"
    )
    print(
        f"Sensor       : HC-SR04 REAL / AWS IoT"
    )
    print(
        f"Cámara       : índice {camera_index}"
    )
    print(
        f"Procesamiento: "
        f"{edge.DEVICE_INFO['mode']} "
        f"({edge.COMPUTE_DEVICE})"
    )
    print(
        f"GPU          : "
        f"{edge.DEVICE_INFO['gpu_name'] or 'CPU'}"
    )
    print(
        f"Backend      : {backend_url}"
    )
    print(
        f"Topic sensor : "
        f"{edge.gate.TOPIC_DETECTION}"
    )
    print(
        "Simulador    : DESACTIVADO"
    )
    print(
        "API local    : "
        "http://127.0.0.1:9000"
    )
    print("=" * 72)
    print()


# ============================================================
# MAIN
# ============================================================

def main():
    camera_index = (
        configure_core()
    )

    disable_demo_routes()

    print_startup(
        camera_index
    )

    # FastAPI local para GuardGate.
    api_thread = threading.Thread(
        target=edge.run_api_server,
        daemon=True,
    )

    api_thread.start()

    time.sleep(
        1.0
    )

    print(
        "[EDGE] Esperando detección REAL "
        "del HC-SR04..."
    )

    print(
        "[EDGE] Cuando AWS IoT reciba "
        "VEHICLE_DETECTED, comenzará "
        "el ciclo automático."
    )

    print()

    try:
        # Core real:
        # MQTT + cámara + tracking + AWS.
        edge.gate.main()

    except KeyboardInterrupt:
        print()
        print(
            "[EDGE] Sistema detenido."
        )


if __name__ == "__main__":
    main()
