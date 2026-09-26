# ============================================================
# SMARTPARK UCE
# DEMOSTRACION LOCAL INTEGRADA
#
# Sensor / MQTT
#      ↓
# YOLO + ByteTrack
#      ↓
# ENTRY / EXIT
#      ↓
# Tiempo para posicionar rostro
#      ↓
# RetinaFace + ArcFace
#      ↓
# Tiempo para posicionar placa
#      ↓
# PaddleOCR
#      ↓
# FastAPI + PostgreSQL
#      ↓
# AUTHORIZED / REJECTED
# ============================================================

import json
import time
import threading
from datetime import datetime, timezone
from pathlib import Path

import cv2
import requests
from ultralytics import YOLO


# ============================================================
# MODULOS SMARTPARK
# ============================================================

try:
    from ai.face_recognition import recognize_face
    from ai.plate_recognition import recognize_plate

except ModuleNotFoundError:
    from face_recognition import recognize_face
    from plate_recognition import recognize_plate


# ============================================================
# MQTT OPCIONAL
# ============================================================

try:
    import paho.mqtt.client as mqtt

    MQTT_AVAILABLE = True

except ImportError:
    MQTT_AVAILABLE = False


# ============================================================
# RUTAS
# ============================================================

AI_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = AI_DIR.parent

MODEL_PATH = PROJECT_ROOT / "yolo11n.pt"

TRACKER_PATH = AI_DIR / "bytetrack_smartpark.yaml"


# ============================================================
# CAMARA
# ============================================================

CAMERA_INDEX = 0

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720


# ============================================================
# YOLO
# ============================================================

VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

CONFIDENCE = 0.15

YOLO_IMAGE_SIZE = 960

IOU_THRESHOLD = 0.50


# ============================================================
# ENTRY / EXIT
# ============================================================

LINE_POSITION = 0.50

LINE_MARGIN = 25

STABLE_FRAMES = 4

EVENT_COOLDOWN = 3.0


# ============================================================
# TIEMPOS PARA TU DEMOSTRACION
# ============================================================

# Tiempo para mover el celular hacia tu rostro.
FACE_PREPARATION_SECONDS = 8

# Tiempo para mover el celular hacia la placa.
PLATE_PREPARATION_SECONDS = 8

# Tiempo que mostramos el resultado final.
SUMMARY_SECONDS = 12


# ============================================================
# BACKEND FASTAPI
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"

AUTHORIZE_URL = (
    f"{API_BASE_URL}/api/v1/access/authorize"
)

ACCESS_EVENTS_URL = (
    f"{API_BASE_URL}/api/v1/access-events"
)

REQUEST_TIMEOUT = 10


# ============================================================
# ASOCIACION ROSTRO -> USUARIO
#
# En PostgreSQL comprobamos:
# Kevin Rueda = user_id 1
# ============================================================

FACE_USER_MAP = {
    "Kevin Rueda": 1,
}


# ============================================================
# MQTT LOCAL
# ============================================================

MQTT_HOST = "localhost"

MQTT_PORT = 1883

MQTT_TOPIC = (
    "smartpark/gates/gate-01/detection"
)

MQTT_COMMAND_TOPIC = (
    "smartpark/gates/gate-01/command"
)

# Segundos que la barrera permanece abierta despues
# de una autorizacion correcta.
BARRIER_OPEN_SECONDS = 5


# ============================================================
# ESTADOS
# ============================================================

STATE_WAIT_SENSOR = "WAIT_SENSOR"

STATE_VEHICLE = "VEHICLE"

STATE_FACE_PREP = "FACE_PREP"

STATE_FACE_ANALYZE = "FACE_ANALYZE"

STATE_PLATE_PREP = "PLATE_PREP"

STATE_PLATE_ANALYZE = "PLATE_ANALYZE"

STATE_AUTHORIZE = "AUTHORIZE"

STATE_SUMMARY = "SUMMARY"


# ============================================================
# VARIABLES GLOBALES
# ============================================================

current_state = STATE_WAIT_SENSOR

state_started_at = time.monotonic()

sensor_trigger = threading.Event()

vehicle_states = {}

direction_result = None

face_result = None

plate_result = None

authorization_result = None


# ============================================================
# CARGAR YOLO
# ============================================================

print()
print("===========================================")
print(" SMARTPARK UCE - DEMOSTRACION LOCAL")
print("===========================================")
print()

print("[YOLO] Cargando YOLO11n...")

model = YOLO(
    str(MODEL_PATH)
)

print("[YOLO] Modelo listo.")


# ============================================================
# CAMBIAR ESTADO
# ============================================================

def change_state(new_state):

    global current_state
    global state_started_at

    current_state = new_state

    state_started_at = time.monotonic()


# ============================================================
# DETERMINAR LADO DE LA LINEA
# ============================================================

def get_side(
    center_y,
    line_y
):

    if center_y < line_y - LINE_MARGIN:
        return -1

    if center_y > line_y + LINE_MARGIN:
        return 1

    return 0


# ============================================================
# REGISTRAR ENTRY / EXIT
# ============================================================

def register_side(
    track_id,
    current_side
):

    if current_side == 0:
        return None


    state = vehicle_states.setdefault(
        track_id,
        {
            "stable_side": None,
            "candidate_side": None,
            "candidate_frames": 0,
            "last_event_time": 0.0,
        }
    )


    if (
        state["candidate_side"]
        != current_side
    ):

        state["candidate_side"] = (
            current_side
        )

        state["candidate_frames"] = 1

    else:

        state["candidate_frames"] += 1


    if (
        state["candidate_frames"]
        < STABLE_FRAMES
    ):
        return None


    previous_side = (
        state["stable_side"]
    )


    if previous_side is None:

        state["stable_side"] = (
            current_side
        )

        return None


    if previous_side == current_side:
        return None


    state["stable_side"] = current_side


    now = time.monotonic()


    if (
        now - state["last_event_time"]
        < EVENT_COOLDOWN
    ):
        return None


    state["last_event_time"] = now


    # ARRIBA -> ABAJO
    if (
        previous_side == -1
        and
        current_side == 1
    ):
        return "ENTRY"


    # ABAJO -> ARRIBA
    if (
        previous_side == 1
        and
        current_side == -1
    ):
        return "EXIT"


    return None


# ============================================================
# RESOLVER VEHICULO PARA EVENTOS RECHAZADOS
# ============================================================

def normalize_plate_value(value):
    """
    Normaliza una placa para compararla con PostgreSQL.
    Ejemplo: TDH-398 -> TDH398
    """

    if not value:
        return None

    return "".join(
        character
        for character in str(value).upper()
        if character.isalnum()
    )


def get_registered_vehicles():
    """
    Consulta los vehiculos registrados en FastAPI.
    Si falla, devuelve una lista vacia.
    """

    try:

        response = requests.get(
            f"{API_BASE_URL}/api/v1/vehicles",
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            return data

        return []

    except Exception as error:

        print(
            f"[EVENT] No se pudieron consultar vehiculos: "
            f"{type(error).__name__}: {error}"
        )

        return []


def resolve_vehicle_context(
    user_id=None,
    detected_plate=None
):
    """
    Intenta obtener vehicle_id y, cuando corresponde,
    el usuario registrado del vehiculo.

    Prioridad:
    1. Si hay placa, buscar por placa.
    2. Si hay usuario y tiene exactamente un vehiculo ACTIVE,
       usar ese vehiculo. Esto es util para el prototipo cuando
       Kevin fue reconocido pero la placa salio borrosa.
    """

    vehicles = get_registered_vehicles()

    normalized_plate = normalize_plate_value(
        detected_plate
    )


    # --------------------------------------------------------
    # 1. BUSCAR POR PLACA
    # --------------------------------------------------------

    if normalized_plate:

        for vehicle in vehicles:

            registered_plate = normalize_plate_value(
                vehicle.get(
                    "plate"
                )
            )

            if (
                registered_plate
                == normalized_plate
            ):

                return {
                    "vehicle_id": vehicle.get(
                        "id"
                    ),
                    "registered_user_id": vehicle.get(
                        "user_id"
                    ),
                }


    # --------------------------------------------------------
    # 2. UNICO VEHICULO ACTIVO DEL USUARIO
    # --------------------------------------------------------

    if user_id is not None:

        user_vehicles = []

        for vehicle in vehicles:

            if (
                vehicle.get(
                    "user_id"
                )
                == user_id
                and
                str(
                    vehicle.get(
                        "status",
                        ""
                    )
                ).upper()
                == "ACTIVE"
            ):

                user_vehicles.append(
                    vehicle
                )


        if len(
            user_vehicles
        ) == 1:

            vehicle = user_vehicles[0]

            return {
                "vehicle_id": vehicle.get(
                    "id"
                ),
                "registered_user_id": vehicle.get(
                    "user_id"
                ),
            }


    return {
        "vehicle_id": None,
        "registered_user_id": None,
    }


# ============================================================
# REGISTRAR RECHAZOS LOCALES
# ============================================================

def register_rejected_event(
    direction,
    reason,
    face_data=None,
    plate_data=None,
    user_id=None,
    vehicle_id=None
):
    """
    Guarda en /api/v1/access-events los rechazos que ocurren
    ANTES de poder llamar a /api/v1/access/authorize.

    Ejemplos:
    - rostro no detectado
    - rostro desconocido
    - placa no detectada
    - placa invalida

    IMPORTANTE:
    /access/authorize ya guarda por si mismo el evento cuando
    se llega hasta el backend. Por eso esta funcion solo se usa
    para rechazos locales y evita duplicar eventos.
    """

    face_score = 0.0
    plate_score = 0.0
    detected_plate = None

    if face_data:
        face_score = float(
            face_data.get(
                "similarity",
                0.0
            )
        )

    if plate_data:
        plate_score = float(
            plate_data.get(
                "confidence",
                0.0
            )
        )

        detected_plate = plate_data.get(
            "plate"
        )


    # --------------------------------------------------------
    # RESOLVER CONTEXTO DEL VEHICULO
    # --------------------------------------------------------

    if vehicle_id is None:

        vehicle_context = resolve_vehicle_context(
            user_id=user_id,
            detected_plate=detected_plate
        )

        vehicle_id = vehicle_context.get(
            "vehicle_id"
        )

        # Si el rostro no fue reconocido pero la placa si
        # pertenece a un vehiculo registrado, usamos el
        # propietario registrado solamente como contexto
        # relacional del evento. La razon seguira indicando
        # claramente que el rostro fue desconocido.
        if (
            user_id is None
            and
            detected_plate
        ):

            user_id = vehicle_context.get(
                "registered_user_id"
            )


    # Si aun no podemos relacionar el evento con usuario y
    # vehiculo, intentamos enviarlo con null. Si el backend
    # actual no permite null, se mostrara el 422 y la demo
    # continuara sin detenerse.

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
        .replace(
            "+00:00",
            "Z"
        )
    )

    evidence_key = (
        "local-rejected-"
        +
        datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d-%H%M%S-%f"
        )
    )

    payload = {
        "timestamp": timestamp,
        "event_type": direction,
        "user_id": user_id,
        "vehicle_id": vehicle_id,
        "detected_plate": detected_plate,
        "face_score": face_score,
        "plate_score": plate_score,
        "decision": "REJECTED",
        "reason": reason,
        "evidence_key": evidence_key,
    }

    print()
    print("================================")
    print("[EVENT] Guardando rechazo local")
    print("================================")
    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False
        )
    )

    try:

        response = requests.post(
            ACCESS_EVENTS_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 422:

            print()
            print(
                "[EVENT] El backend no acepto el evento "
                "(HTTP 422)."
            )
            print(
                "[EVENT] Probablemente user_id o vehicle_id "
                "no admiten null en el esquema actual."
            )
            print(
                "[EVENT] La demostracion continuara normalmente."
            )
            print(
                f"[EVENT] Detalle: {response.text}"
            )

            return {
                "saved": False,
                "status_code": response.status_code,
                "detail": response.text,
            }

        response.raise_for_status()

        try:
            saved_event = response.json()
        except Exception:
            saved_event = None

        print(
            "[EVENT] Rechazo guardado en PostgreSQL."
        )

        return {
            "saved": True,
            "event": saved_event,
        }

    except requests.exceptions.ConnectionError:

        print(
            "[EVENT] No se pudo conectar con FastAPI "
            "para guardar el rechazo."
        )

        return {
            "saved": False,
            "detail": "FastAPI unavailable",
        }

    except requests.exceptions.Timeout:

        print(
            "[EVENT] Timeout guardando el rechazo."
        )

        return {
            "saved": False,
            "detail": "Timeout",
        }

    except Exception as error:

        print(
            f"[EVENT] Error guardando rechazo: "
            f"{type(error).__name__}: {error}"
        )

        return {
            "saved": False,
            "detail": str(error),
        }


# ============================================================
# AUTORIZACION FASTAPI
# ============================================================

def authorize_access(
    direction,
    face_data,
    plate_data
):
    """
    Toma los resultados de IA y llama al backend.

    Si rostro y placa son validos, usa:
        POST /api/v1/access/authorize

    Ese endpoint ya guarda el evento AUTHORIZED/REJECTED.

    Si el flujo falla antes de poder llamar a /authorize,
    registramos manualmente un REJECTED con:
        POST /api/v1/access-events
    """

    # --------------------------------------------------------
    # VALIDAR ROSTRO
    # --------------------------------------------------------

    if not face_data:

        reason = "No facial result available"

        register_rejected_event(
            direction=direction,
            reason=reason,
            face_data=None,
            plate_data=plate_data,
            user_id=None,
            vehicle_id=None
        )

        return {
            "decision": "REJECTED",
            "reason": reason,
            "source": "LOCAL",
        }


    if not face_data.get(
        "recognized",
        False
    ):

        reason = "Face not recognized"

        register_rejected_event(
            direction=direction,
            reason=reason,
            face_data=face_data,
            plate_data=plate_data,
            user_id=None,
            vehicle_id=None
        )

        return {
            "decision": "REJECTED",
            "reason": reason,
            "source": "LOCAL",
        }


    face_name = face_data.get(
        "name"
    )


    # --------------------------------------------------------
    # BUSCAR USER_ID
    # --------------------------------------------------------

    user_id = FACE_USER_MAP.get(
        face_name
    )


    if user_id is None:

        reason = (
            f"No user_id associated "
            f"with face '{face_name}'"
        )

        register_rejected_event(
            direction=direction,
            reason=reason,
            face_data=face_data,
            plate_data=plate_data,
            user_id=None,
            vehicle_id=None
        )

        return {
            "decision": "REJECTED",
            "reason": reason,
            "source": "LOCAL",
        }


    # --------------------------------------------------------
    # VALIDAR PLACA
    # --------------------------------------------------------

    if not plate_data:

        reason = "No plate result available"

        register_rejected_event(
            direction=direction,
            reason=reason,
            face_data=face_data,
            plate_data=None,
            user_id=user_id,
            vehicle_id=None
        )

        return {
            "decision": "REJECTED",
            "reason": reason,
            "source": "LOCAL",
        }


    if not plate_data.get(
        "detected",
        False
    ):

        reason = "License plate not detected"

        register_rejected_event(
            direction=direction,
            reason=reason,
            face_data=face_data,
            plate_data=plate_data,
            user_id=user_id,
            vehicle_id=None
        )

        return {
            "decision": "REJECTED",
            "reason": reason,
            "source": "LOCAL",
        }


    detected_plate = plate_data.get(
        "plate"
    )


    if not detected_plate:

        reason = "Invalid license plate"

        register_rejected_event(
            direction=direction,
            reason=reason,
            face_data=face_data,
            plate_data=plate_data,
            user_id=user_id,
            vehicle_id=None
        )

        return {
            "decision": "REJECTED",
            "reason": reason,
            "source": "LOCAL",
        }


    # --------------------------------------------------------
    # CREAR EVIDENCE KEY TEMPORAL
    # --------------------------------------------------------

    evidence_key = (
        "local-demo-"
        +
        datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d-%H%M%S-%f"
        )
    )


    # --------------------------------------------------------
    # JSON PARA FASTAPI
    # --------------------------------------------------------

    payload = {
        "user_id": user_id,

        "detected_plate":
            detected_plate,

        "event_type":
            direction,

        "face_score":
            float(
                face_data.get(
                    "similarity",
                    0.0
                )
            ),

        "plate_score":
            float(
                plate_data.get(
                    "confidence",
                    0.0
                )
            ),

        "evidence_key":
            evidence_key,
    }


    print()
    print("================================")
    print("[BACKEND] Enviando autorizacion")
    print("================================")

    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False
        )
    )


    # --------------------------------------------------------
    # PETICION HTTP
    # --------------------------------------------------------

    try:

        response = requests.post(
            AUTHORIZE_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        data["source"] = "BACKEND"

        return data


    except requests.exceptions.ConnectionError:

        return {
            "decision": "ERROR",
            "reason": (
                "No se pudo conectar con FastAPI. "
                "Verifica que el backend este activo."
            ),
            "source": "LOCAL",
        }


    except requests.exceptions.Timeout:

        return {
            "decision": "ERROR",
            "reason": (
                "FastAPI no respondio a tiempo."
            ),
            "source": "LOCAL",
        }


    except requests.exceptions.HTTPError as error:

        try:
            detail = response.text

        except Exception:
            detail = str(error)


        return {
            "decision": "ERROR",
            "reason": (
                f"HTTP error: {detail}"
            ),
            "source": "LOCAL",
        }


    except Exception as error:

        return {
            "decision": "ERROR",
            "reason": (
                f"{type(error).__name__}: "
                f"{error}"
            ),
            "source": "LOCAL",
        }


# ============================================================
# MQTT
# ============================================================

def mqtt_on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties=None
):

    print(
        "[MQTT] Conectado al broker local."
    )

    client.subscribe(
        MQTT_TOPIC
    )

    print(
        f"[MQTT] Escuchando: "
        f"{MQTT_TOPIC}"
    )


def mqtt_on_message(
    client,
    userdata,
    message
):

    try:

        payload = json.loads(
            message.payload.decode(
                "utf-8"
            )
        )


        event = payload.get(
            "event"
        )


        if (
            event
            == "VEHICLE_DETECTED"
        ):

            print()
            print(
                "[SENSOR] Vehiculo detectado."
            )

            sensor_trigger.set()


    except Exception as error:

        print(
            f"[MQTT] Mensaje invalido: "
            f"{error}"
        )


# ============================================================
# INICIAR MQTT
# ============================================================

def start_mqtt():

    if not MQTT_AVAILABLE:

        print(
            "[MQTT] paho-mqtt no instalado."
        )

        print(
            "[MQTT] Usa S para simular "
            "el sensor."
        )

        return None


    try:

        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2
        )


        client.on_connect = (
            mqtt_on_connect
        )

        client.on_message = (
            mqtt_on_message
        )


        client.connect(
            MQTT_HOST,
            MQTT_PORT,
            60
        )


        client.loop_start()


        return client


    except Exception as error:

        print(
            f"[MQTT] No se pudo conectar: "
            f"{error}"
        )

        print(
            "[MQTT] Usa S para simular "
            "el sensor."
        )

        return None


# ============================================================
# CONTROL DE BARRERA POR MQTT
# ============================================================

def publish_barrier_command(
    mqtt_client,
    command
):
    """
    Publica OPEN o CLOSE para el ESP32/SG90 real o simulado.
    """

    if mqtt_client is None:

        print(
            "[BARRIER] MQTT no disponible. "
            "No se pudo enviar el comando."
        )

        return False


    command = str(command).upper().strip()


    if command not in ("OPEN", "CLOSE"):

        print(
            f"[BARRIER] Comando invalido: {command}"
        )

        return False


    payload = {
        "command": command
    }


    try:

        info = mqtt_client.publish(
            MQTT_COMMAND_TOPIC,
            json.dumps(payload),
            qos=1
        )

        print()
        print(
            f"[BARRIER] Comando enviado: {command}"
        )
        print(
            f"[BARRIER] Topic: {MQTT_COMMAND_TOPIC}"
        )

        # Espera solo a que el mensaje salga del cliente MQTT;
        # no bloquea durante los segundos que la barrera queda abierta.
        try:
            info.wait_for_publish(timeout=2.0)
        except Exception:
            pass

        return True


    except Exception as error:

        print(
            f"[BARRIER] Error publicando {command}: "
            f"{type(error).__name__}: {error}"
        )

        return False



def schedule_barrier_close(
    mqtt_client,
    delay_seconds=BARRIER_OPEN_SECONDS
):
    """
    Programa CLOSE sin congelar la camara ni la interfaz.
    """

    def close_later():

        print()
        print(
            f"[BARRIER] Tiempo cumplido "
            f"({delay_seconds}s). Cerrando..."
        )

        publish_barrier_command(
            mqtt_client,
            "CLOSE"
        )


    timer = threading.Timer(
        delay_seconds,
        close_later
    )

    timer.daemon = True

    timer.start()

    return timer


# ============================================================
# DIBUJAR TEXTO
# ============================================================

def draw_text(
    frame,
    text,
    y,
    color=(255, 255, 255),
    scale=0.75
):

    cv2.putText(
        frame,
        text,
        (
            30,
            y
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        2
    )


# ============================================================
# CUENTA REGRESIVA
# ============================================================

def countdown_remaining(
    total_seconds
):

    elapsed = (
        time.monotonic()
        -
        state_started_at
    )


    remaining = int(
        total_seconds
        -
        elapsed
        +
        1
    )


    return max(
        remaining,
        0
    )


# ============================================================
# REINICIAR SESION
# ============================================================

def reset_session():

    global direction_result
    global face_result
    global plate_result
    global authorization_result
    global vehicle_states


    direction_result = None

    face_result = None

    plate_result = None

    authorization_result = None

    vehicle_states = {}


    sensor_trigger.clear()


    change_state(
        STATE_WAIT_SENSOR
    )


    print()
    print(
        "==========================================="
    )

    print(
        "[SMARTPARK] Listo para nuevo vehiculo."
    )

    print(
        "==========================================="
    )

    print()


# ============================================================
# MAIN
# ============================================================

def main():

    global direction_result
    global face_result
    global plate_result
    global authorization_result


    mqtt_client = start_mqtt()


    # ========================================================
    # CAMARA
    # ========================================================

    print()
    print(
        "[CAMERA] Abriendo DroidCam..."
    )


    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )


    if not camera.isOpened():

        print(
            "[CAMERA] No se pudo abrir DroidCam."
        )

        return


    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )


    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )


    camera.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )


    print(
        "[CAMERA] DroidCam listo."
    )


    print()
    print(
        "S = simular sensor"
    )

    print(
        "Q = salir"
    )

    print()


    # ========================================================
    # LOOP PRINCIPAL
    # ========================================================

    while True:

        success, frame = camera.read()


        if not success:

            print(
                "[CAMERA] Error leyendo frame."
            )

            break


        frame_height, frame_width = (
            frame.shape[:2]
        )


        now = time.monotonic()


        # ====================================================
        # 1. ESPERAR SENSOR
        # ====================================================

        if (
            current_state
            == STATE_WAIT_SENSOR
        ):

            draw_text(
                frame,
                "SMARTPARK UCE",
                45,
                (
                    255,
                    255,
                    255
                ),
                0.9
            )


            draw_text(
                frame,
                "ESPERANDO VEHICULO...",
                90,
                (
                    0,
                    255,
                    255
                ),
                0.8
            )


            draw_text(
                frame,
                "Sensor HC-SR04 / MQTT",
                130
            )


            draw_text(
                frame,
                "S = simular sensor",
                170,
                (
                    150,
                    150,
                    150
                ),
                0.6
            )


            if sensor_trigger.is_set():

                vehicle_states.clear()

                change_state(
                    STATE_VEHICLE
                )


                print()
                print(
                    "[SMARTPARK] Iniciando "
                    "deteccion vehicular..."
                )


        # ====================================================
        # 2. VEHICULO
        # ====================================================

        elif (
            current_state
            == STATE_VEHICLE
        ):

            line_y = int(
                frame_height
                *
                LINE_POSITION
            )


            cv2.line(
                frame,
                (
                    0,
                    line_y
                ),
                (
                    frame_width,
                    line_y
                ),
                (
                    255,
                    0,
                    0
                ),
                3
            )


            draw_text(
                frame,
                "VEHICULO DETECTADO",
                45,
                (
                    0,
                    255,
                    255
                )
            )


            draw_text(
                frame,
                "Mueve el vehiculo cruzando la linea",
                80
            )


            results = model.track(
                source=frame,

                persist=True,

                tracker=str(
                    TRACKER_PATH
                ),

                classes=list(
                    VEHICLE_CLASSES.keys()
                ),

                conf=CONFIDENCE,

                iou=IOU_THRESHOLD,

                imgsz=YOLO_IMAGE_SIZE,

                verbose=False
            )


            event_found = False


            for result in results:

                if result.boxes is None:
                    continue


                for box in result.boxes:

                    if box.id is None:
                        continue


                    class_id = int(
                        box.cls[0]
                    )


                    if (
                        class_id
                        not in VEHICLE_CLASSES
                    ):
                        continue


                    track_id = int(
                        box.id[0]
                    )


                    confidence = float(
                        box.conf[0]
                    )


                    (
                        x1,
                        y1,
                        x2,
                        y2
                    ) = map(
                        int,
                        box.xyxy[0]
                    )


                    center_y = int(
                        (
                            y1 + y2
                        )
                        / 2
                    )


                    cv2.rectangle(
                        frame,
                        (
                            x1,
                            y1
                        ),
                        (
                            x2,
                            y2
                        ),
                        (
                            0,
                            255,
                            0
                        ),
                        2
                    )


                    label = (
                        f"{VEHICLE_CLASSES[class_id]} "
                        f"ID:{track_id} "
                        f"{confidence:.2f}"
                    )


                    cv2.putText(
                        frame,
                        label,
                        (
                            x1,
                            max(
                                y1 - 10,
                                30
                            )
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (
                            0,
                            255,
                            0
                        ),
                        2
                    )


                    side = get_side(
                        center_y,
                        line_y
                    )


                    movement = register_side(
                        track_id,
                        side
                    )


                    if movement:

                        direction_result = (
                            movement
                        )


                        print()
                        print(
                            "================================"
                        )

                        print(
                            f"[VEHICLE] {movement}"
                        )

                        print(
                            "================================"
                        )


                        change_state(
                            STATE_FACE_PREP
                        )


                        event_found = True

                        break


                if event_found:
                    break


        # ====================================================
        # 3. PREPARAR ROSTRO
        # ====================================================

        elif (
            current_state
            == STATE_FACE_PREP
        ):

            remaining = countdown_remaining(
                FACE_PREPARATION_SECONDS
            )


            draw_text(
                frame,
                f"VEHICULO: {direction_result}",
                45,
                (
                    0,
                    255,
                    0
                )
            )


            draw_text(
                frame,
                "AHORA COLOCA LA CAMARA",
                100,
                (
                    0,
                    255,
                    255
                ),
                0.8
            )


            draw_text(
                frame,
                "FRENTE A TU ROSTRO",
                145,
                (
                    0,
                    255,
                    255
                ),
                0.9
            )


            draw_text(
                frame,
                f"Captura facial en: {remaining}",
                210,
                (
                    255,
                    255,
                    255
                ),
                1.0
            )


            if remaining <= 0:

                change_state(
                    STATE_FACE_ANALYZE
                )


        # ====================================================
        # 4. ANALIZAR ROSTRO
        # ====================================================

        elif (
            current_state
            == STATE_FACE_ANALYZE
        ):

            draw_text(
                frame,
                "ANALIZANDO ROSTRO...",
                80,
                (
                    0,
                    255,
                    255
                ),
                0.9
            )


            cv2.imshow(
                "SmartPark UCE - Demo Local",
                frame
            )

            cv2.waitKey(1)


            print()
            print(
                "[FACE] Analizando rostro..."
            )


            face_result = recognize_face(
                frame.copy()
            )


            print(
                f"[FACE] Resultado: "
                f"{face_result.get('name')}"
            )


            print(
                f"[FACE] Similitud: "
                f"{face_result.get('similarity', 0) * 100:.2f}%"
            )


            change_state(
                STATE_PLATE_PREP
            )


        # ====================================================
        # 5. PREPARAR PLACA
        # ====================================================

        elif (
            current_state
            == STATE_PLATE_PREP
        ):

            remaining = countdown_remaining(
                PLATE_PREPARATION_SECONDS
            )


            name = (
                face_result.get(
                    "name",
                    "SIN ROSTRO"
                )
                if face_result
                else "SIN ROSTRO"
            )


            draw_text(
                frame,
                f"ROSTRO: {name}",
                45,
                (
                    0,
                    255,
                    0
                )
            )


            draw_text(
                frame,
                "AHORA MUEVE LA CAMARA",
                100,
                (
                    0,
                    255,
                    255
                ),
                0.8
            )


            draw_text(
                frame,
                "HACIA LA PLACA",
                145,
                (
                    0,
                    255,
                    255
                ),
                0.9
            )


            draw_text(
                frame,
                f"Lectura de placa en: {remaining}",
                220,
                (
                    255,
                    255,
                    255
                ),
                1.0
            )


            if remaining <= 0:

                change_state(
                    STATE_PLATE_ANALYZE
                )


        # ====================================================
        # 6. ANALIZAR PLACA
        # ====================================================

        elif (
            current_state
            == STATE_PLATE_ANALYZE
        ):

            draw_text(
                frame,
                "BUSCANDO MATRICULA...",
                80,
                (
                    0,
                    255,
                    255
                ),
                0.9
            )


            cv2.imshow(
                "SmartPark UCE - Demo Local",
                frame
            )

            cv2.waitKey(1)


            print()
            print(
                "[PLATE] Analizando escena..."
            )


            plate_result = recognize_plate(
                frame.copy()
            )


            if plate_result.get(
                "detected",
                False
            ):

                print(
                    f"[PLATE] Matricula: "
                    f"{plate_result['plate_display']}"
                )

                print(
                    f"[PLATE] Confianza: "
                    f"{plate_result['confidence'] * 100:.2f}%"
                )

            else:

                print(
                    "[PLATE] No se encontro matricula."
                )


            change_state(
                STATE_AUTHORIZE
            )


        # ====================================================
        # 7. AUTORIZAR CONTRA FASTAPI
        # ====================================================

        elif (
            current_state
            == STATE_AUTHORIZE
        ):

            draw_text(
                frame,
                "VERIFICANDO AUTORIZACION...",
                80,
                (
                    0,
                    255,
                    255
                ),
                0.9
            )


            cv2.imshow(
                "SmartPark UCE - Demo Local",
                frame
            )

            cv2.waitKey(1)


            authorization_result = (
                authorize_access(
                    direction_result,
                    face_result,
                    plate_result
                )
            )


            decision = (
                authorization_result.get(
                    "decision",
                    "ERROR"
                )
            )


            reason = (
                authorization_result.get(
                    "reason",
                    "Sin detalle"
                )
            )


            print()
            print(
                "================================"
            )

            print(
                f"[ACCESS] DECISION: {decision}"
            )

            print(
                f"[ACCESS] MOTIVO: {reason}"
            )

            print(
                "================================"
            )


            # =================================================
            # CONTROL AUTOMATICO DE BARRERA
            # =================================================

            if decision == "AUTHORIZED":

                print()
                print(
                    "[BARRIER] Acceso autorizado. "
                    "Abriendo barrera..."
                )

                opened = publish_barrier_command(
                    mqtt_client,
                    "OPEN"
                )

                if opened:

                    print(
                        f"[BARRIER] Se cerrara "
                        f"automaticamente en "
                        f"{BARRIER_OPEN_SECONDS} segundos."
                    )

                    schedule_barrier_close(
                        mqtt_client,
                        BARRIER_OPEN_SECONDS
                    )


            elif decision == "REJECTED":

                print()
                print(
                    "[BARRIER] Acceso rechazado. "
                    "La barrera permanece cerrada."
                )

                # Refuerza el estado seguro. Si ya esta cerrada,
                # el ESP32 simulado simplemente lo indicara.
                publish_barrier_command(
                    mqtt_client,
                    "CLOSE"
                )


            else:

                print()
                print(
                    "[BARRIER] No se envia OPEN porque "
                    "la autorizacion termino con ERROR."
                )


            change_state(
                STATE_SUMMARY
            )


        # ====================================================
        # 8. RESUMEN FINAL
        # ====================================================

        elif (
            current_state
            == STATE_SUMMARY
        ):

            elapsed = (
                now
                -
                state_started_at
            )


            face_name = (
                face_result.get(
                    "name",
                    "SIN ROSTRO"
                )
                if face_result
                else "SIN ROSTRO"
            )


            face_similarity = (
                face_result.get(
                    "similarity",
                    0.0
                )
                if face_result
                else 0.0
            )


            if (
                plate_result
                and
                plate_result.get(
                    "detected",
                    False
                )
            ):

                plate_text = (
                    plate_result.get(
                        "plate_display",
                        "NO DETECTADA"
                    )
                )


                plate_confidence = (
                    plate_result.get(
                        "confidence",
                        0.0
                    )
                )

            else:

                plate_text = (
                    "NO DETECTADA"
                )

                plate_confidence = 0.0


            decision = (
                authorization_result.get(
                    "decision",
                    "ERROR"
                )
                if authorization_result
                else "ERROR"
            )


            reason = (
                authorization_result.get(
                    "reason",
                    "Sin respuesta"
                )
                if authorization_result
                else "Sin respuesta"
            )


            # -----------------------------------------------
            # COLOR DE DECISION
            # -----------------------------------------------

            if decision == "AUTHORIZED":

                decision_color = (
                    0,
                    255,
                    0
                )

            elif decision == "REJECTED":

                decision_color = (
                    0,
                    0,
                    255
                )

            else:

                decision_color = (
                    0,
                    255,
                    255
                )


            # -----------------------------------------------
            # PANTALLA
            # -----------------------------------------------

            draw_text(
                frame,
                "RESULTADO SMARTPARK",
                50,
                (
                    255,
                    255,
                    255
                ),
                1.0
            )


            draw_text(
                frame,
                f"MOVIMIENTO: {direction_result}",
                110,
                (
                    0,
                    255,
                    0
                ),
                0.85
            )


            draw_text(
                frame,
                f"ROSTRO: {face_name}",
                160,
                (
                    0,
                    255,
                    0
                ),
                0.85
            )


            draw_text(
                frame,
                f"SIMILITUD: "
                f"{face_similarity * 100:.2f}%",
                200
            )


            draw_text(
                frame,
                f"MATRICULA: {plate_text}",
                250,
                (
                    0,
                    255,
                    0
                ),
                0.85
            )


            if plate_confidence > 0:

                draw_text(
                    frame,
                    f"CONFIANZA OCR: "
                    f"{plate_confidence * 100:.2f}%",
                    290
                )


            draw_text(
                frame,
                f"AUTORIZACION: {decision}",
                355,
                decision_color,
                1.05
            )


            draw_text(
                frame,
                f"MOTIVO: {reason}",
                405,
                decision_color,
                0.55
            )


            draw_text(
                frame,
                "Nueva sesion automaticamente...",
                460,
                (
                    180,
                    180,
                    180
                ),
                0.55
            )


            # -----------------------------------------------
            # REINICIAR
            # -----------------------------------------------

            if (
                elapsed
                >= SUMMARY_SECONDS
            ):

                reset_session()


        # ====================================================
        # MOSTRAR CAMARA
        # ====================================================

        cv2.imshow(
            "SmartPark UCE - Demo Local",
            frame
        )


        key = (
            cv2.waitKey(1)
            & 0xFF
        )


        # ====================================================
        # S = SIMULAR SENSOR
        # ====================================================

        if (
            key == ord("s")
            and
            current_state
            == STATE_WAIT_SENSOR
        ):

            print()
            print(
                "[SENSOR] Vehiculo detectado "
                "(SIMULACION LOCAL)"
            )

            sensor_trigger.set()


        # ====================================================
        # Q = SALIR
        # ====================================================

        if key == ord("q"):
            break


    # ========================================================
    # CERRAR
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()


    if mqtt_client:

        mqtt_client.loop_stop()

        mqtt_client.disconnect()


    print()
    print(
        "[SMARTPARK] Sistema detenido."
    )


# ============================================================
# EJECUCION
# ============================================================

if __name__ == "__main__":

    main()