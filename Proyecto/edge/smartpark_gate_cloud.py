import cv2
import httpx
import json
import threading
import time
from datetime import datetime
from pathlib import Path

from ultralytics import YOLO
from awscrt import mqtt
from awsiot import mqtt_connection_builder


# ============================================================
# SMARTPARK UCE
# SERVICIO EDGE / GARITA
# ============================================================
#
# HC-SR04
#    ↓
# ESP32
#    ↓
# AWS IoT Core
#    ↓
# VEHICLE_DETECTED
#    ↓
# DroidCam
#    ↓
# YOLO11n + ByteTrack
#    ↓
# ENTRY / EXIT
#    ↓
# Espera de posicionamiento
#    ↓
# Detección local de rostro + estabilidad + nitidez
#    ↓
# Espera de posicionamiento
#    ↓
# Detección local de placa + estabilidad + nitidez
#    ↓
# Backend 1.6 /api/v1/access/process
#    ↓
# IA 2.7: ArcFace + RetinaFace + OCR 1.1
#    ↓
# RDS + AWS IoT
#    ↓
# Barrera
#
# ============================================================


# ============================================================
# BACKEND AWS
# ============================================================
BACKEND_BASE_URL = "http://44.193.218.178:8000"
HEALTH_URL = f"{BACKEND_BASE_URL}/health"
PROCESS_URL = f"{BACKEND_BASE_URL}/api/v1/access/process"


# ============================================================
# AWS IOT
# ============================================================

AWS_IOT_ENDPOINT = "a3e93abira4kkd-ats.iot.us-east-1.amazonaws.com"
MQTT_CLIENT_ID = "smartpark-camera-01"
TOPIC_DETECTION = "smartpark/gates/gate-01/detection"

ROOT_CA = "certs/camera/AmazonRootCA1.pem"
CERTIFICATE = "certs/camera/camera-certificate.pem.crt"
PRIVATE_KEY = "certs/camera/camera-private.pem.key"


# ============================================================
# CÁMARA
# ============================================================

CAMERA_SOURCE = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
WINDOW_NAME = "SmartPark UCE - Acceso"


# ============================================================
# YOLO + BYTETRACK
# ============================================================

YOLO_MODEL_PATH = str(Path(__file__).resolve().parent / "models" / "yolo11n.pt")

# COCO: car, motorcycle, bus, truck
VEHICLE_CLASSES = [2, 3, 5, 7]
TRACK_CONFIDENCE = 0.30
LINE_POSITION = 0.50
LINE_MARGIN = 25
TRACK_PREPARE_SECONDS = 3
TRACK_MAX_SECONDS = 25


# ============================================================
# CAPTURA FACIAL
# ============================================================
#
# Primero damos tiempo para colocarse frente a la cámara.
# Después NO capturamos en cuanto aparece la primera cara.
# Exigimos:
#   - cara suficientemente grande
#   - cara centrada
#   - nitidez mínima
#   - estabilidad durante FACE_STABLE_SECONDS
# Durante ese intervalo guardamos el frame más nítido.
# ============================================================

FACE_REPOSITION_SECONDS = 4
FACE_SEARCH_TIMEOUT_SECONDS = 45
FACE_STABLE_SECONDS = 1.8
FACE_MIN_SHARPNESS = 120.0
FACE_MIN_WIDTH_RATIO = 0.16
FACE_MAX_WIDTH_RATIO = 0.72
FACE_CENTER_TOLERANCE_X = 0.22
FACE_CENTER_TOLERANCE_Y = 0.24
FACE_CONFIRM_SECONDS = 1.2


# ============================================================
# CAPTURA DE PLACA
# ============================================================
#
# Como en la demostración se usa una sola cámara, damos más
# tiempo para girarla/apuntarla después de capturar el rostro.
# No se captura apenas aparece una forma rectangular: exigimos
# estabilidad y nitidez y guardamos el mejor frame COMPLETO.
# El OCR real se realiza en AWS.
# ============================================================

PLATE_REPOSITION_SECONDS = 6
PLATE_SEARCH_TIMEOUT_SECONDS = 50
PLATE_STABLE_SECONDS = 1.8
PLATE_MIN_SHARPNESS = 150.0
PLATE_MIN_WIDTH_RATIO = 0.16
PLATE_MAX_WIDTH_RATIO = 0.75
PLATE_CENTER_TOLERANCE_X = 0.30
PLATE_CENTER_TOLERANCE_Y = 0.32
PLATE_CONFIRM_SECONDS = 1.2


# ============================================================
# RESULTADO FINAL
# ============================================================

FINAL_RESULT_SECONDS = 5


# ============================================================
# ESTADO GLOBAL
# ============================================================

vehicle_event = threading.Event()
processing = False
last_distance = None
mqtt_connection = None
status_message = "ESPERANDO VEHICULO..."
status_color = (255, 255, 255)


# ============================================================
# TRACKER
# ============================================================

def get_tracker_path():
    possible_paths = [
        Path(__file__).resolve().parent / "bytetrack_smartpark.yaml",
        Path("ai/bytetrack_smartpark.yaml"),
        Path("bytetrack_smartpark.yaml"),
        Path("ai/bytetrack.yaml"),
    ]

    for path in possible_paths:
        if path.exists():
            print(f"[TRACKING] Tracker: {path}")
            return str(path)

    print("[TRACKING] No se encontró bytetrack_smartpark.yaml.")
    print("[TRACKING] Se usará bytetrack.yaml de Ultralytics.")
    return "bytetrack.yaml"


TRACKER_CONFIG = get_tracker_path()


# ============================================================
# CARGAR MODELOS LOCALES
# ============================================================

print()
print("=" * 72)
print("[YOLO] Cargando YOLO11n...")
print("=" * 72)

yolo_model = YOLO(YOLO_MODEL_PATH)
print("[YOLO] YOLO11n listo ✅")


# Haar local: SOLO detección, no reconocimiento biométrico.
FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)

if face_cascade.empty():
    raise RuntimeError("No se pudo cargar el detector local de rostros de OpenCV.")


# Si existe, usamos el cascade de matrículas como primera opción.
PLATE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_russian_plate_number.xml"
plate_cascade = cv2.CascadeClassifier(PLATE_CASCADE_PATH)
PLATE_CASCADE_AVAILABLE = not plate_cascade.empty()

if PLATE_CASCADE_AVAILABLE:
    print("[PLATE] Detector local de matrículas OpenCV listo ✅")
else:
    print("[PLATE] Cascade de matrículas no disponible; se usará detector geométrico.")


# ============================================================
# UTILIDADES
# ============================================================

def separator():
    print()
    print("=" * 72)


def frame_to_jpeg(frame):
    success, encoded = cv2.imencode(
        ".jpg",
        frame,
        [int(cv2.IMWRITE_JPEG_QUALITY), 92],
    )

    if not success:
        raise RuntimeError("No se pudo convertir el frame a JPEG.")

    return encoded.tobytes()


def sharpness_score(image):
    if image is None or image.size == 0:
        return 0.0

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def box_centered(box, frame_shape, tolerance_x, tolerance_y):
    x, y, w, h = box
    frame_h, frame_w = frame_shape[:2]

    center_x = x + (w / 2.0)
    center_y = y + (h / 2.0)

    frame_center_x = frame_w / 2.0
    frame_center_y = frame_h / 2.0

    dx = abs(center_x - frame_center_x) / frame_w
    dy = abs(center_y - frame_center_y) / frame_h

    return dx <= tolerance_x and dy <= tolerance_y


def crop_with_margin(frame, box, margin=0.12):
    x, y, w, h = box
    frame_h, frame_w = frame.shape[:2]

    mx = int(w * margin)
    my = int(h * margin)

    x1 = max(0, x - mx)
    y1 = max(0, y - my)
    x2 = min(frame_w, x + w + mx)
    y2 = min(frame_h, y + h + my)

    return frame[y1:y2, x1:x2]


def show_stage_countdown(camera, seconds, title, subtitle):
    """Tiempo de gracia para mover cámara/persona antes de detectar."""
    for remaining in range(seconds, 0, -1):
        second_start = time.time()

        while time.time() - second_start < 1.0:
            success, frame = camera.read()
            if not success or frame is None:
                continue

            display = frame.copy()
            draw_header(
                display,
                f"{title} {remaining}",
                subtitle,
                (0, 255, 255),
            )

            cv2.putText(
                display,
                str(remaining),
                (display.shape[1] // 2 - 35, display.shape[0] // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                2.8,
                (0, 255, 255),
                6,
            )

            cv2.imshow(WINDOW_NAME, display)
            cv2.waitKey(1)


# ============================================================
# BACKEND HEALTH
# ============================================================

def check_cloud():
    separator()
    print("[CLOUD] Comprobando Backend AWS...")
    print(f"[CLOUD] {HEALTH_URL}")

    try:
        response = httpx.get(HEALTH_URL, timeout=15.0)
        response.raise_for_status()
        result = response.json()

        print("[CLOUD] BACKEND AWS DISPONIBLE ✅")
        print(result)
        return True

    except Exception as error:
        print("[CLOUD] BACKEND AWS NO DISPONIBLE ❌")
        print(error)
        return False


# ============================================================
# MQTT CALLBACK
# ============================================================

def on_mqtt_message(topic, payload, dup, qos, retain, **kwargs):
    global last_distance
    global status_message
    global status_color
    global processing

    try:
        message = json.loads(payload.decode("utf-8"))
        event = message.get("event")
        distance = message.get("distance_cm")

        if event != "VEHICLE_DETECTED":
            return

        if processing:
            print("[AWS IOT] Evento ignorado: SmartPark ya está procesando.")
            return

        last_distance = distance

        separator()
        print("🚗 VEHICLE_DETECTED")
        print(f"[HC-SR04] Distancia: {distance} cm")

        status_message = f"VEHICULO DETECTADO {distance} cm"
        status_color = (0, 255, 255)
        vehicle_event.set()

    except Exception as error:
        print("[MQTT] Error:")
        print(error)


# ============================================================
# AWS IOT
# ============================================================

def connect_mqtt():
    global mqtt_connection

    separator()
    print("[AWS IOT] Conectando...")

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=AWS_IOT_ENDPOINT,
        cert_filepath=CERTIFICATE,
        pri_key_filepath=PRIVATE_KEY,
        ca_filepath=ROOT_CA,
        client_id=MQTT_CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
    )

    mqtt_connection.connect().result()
    print("[AWS IOT] CONECTADO ✅")

    subscribe_future, _ = mqtt_connection.subscribe(
        topic=TOPIC_DETECTION,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_mqtt_message,
    )

    subscribe_future.result()
    print("[AWS IOT] SUSCRIPCIÓN ACTIVA ✅")
    print(f"[AWS IOT] Topic: {TOPIC_DETECTION}")


# ============================================================
# CÁMARA
# ============================================================

def open_camera():
    separator()
    print("[CAMERA] Abriendo DroidCam...")

    camera = cv2.VideoCapture(CAMERA_SOURCE)

    if not camera.isOpened():
        print("[CAMERA] No se pudo abrir DroidCam.")
        return None

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    time.sleep(1.0)
    success, frame = camera.read()

    if not success or frame is None:
        camera.release()
        print("[CAMERA] DroidCam abrió pero no entrega frames.")
        return None

    print("[CAMERA] DroidCam lista ✅")
    print(f"[CAMERA] Resolución: {frame.shape[1]}x{frame.shape[0]}")
    return camera


# ============================================================
# DIBUJO UI
# ============================================================

def draw_header(frame, title, subtitle="", title_color=(255, 255, 255)):
    height, width = frame.shape[:2]

    cv2.rectangle(frame, (0, 0), (width, 120), (0, 0, 0), -1)

    cv2.putText(
        frame,
        "SMARTPARK UCE",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        title,
        (20, 72),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.68,
        title_color,
        2,
    )

    if subtitle:
        cv2.putText(
            frame,
            subtitle,
            (20, 103),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (255, 255, 255),
            1,
        )

    now = datetime.now().strftime("%H:%M:%S")

    cv2.putText(
        frame,
        now,
        (max(20, width - 105), 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (255, 255, 255),
        1,
    )


def draw_tracking_line(frame):
    height, width = frame.shape[:2]
    line_y = int(height * LINE_POSITION)

    cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 255), 3)

    cv2.putText(
        frame,
        "LINEA DE CONTROL",
        (20, line_y - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        "ARRIBA",
        (width - 120, line_y - 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (255, 255, 0),
        2,
    )

    cv2.putText(
        frame,
        "ABAJO",
        (width - 120, line_y + 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (0, 255, 0),
        2,
    )

    return line_y


def get_side(center_y, line_y):
    if center_y < line_y - LINE_MARGIN:
        return "ABOVE"

    if center_y > line_y + LINE_MARGIN:
        return "BELOW"

    return None


def reset_tracker():
    try:
        yolo_model.predictor = None
        print("[TRACKING] Estado reiniciado.")
    except Exception:
        pass


# ============================================================
# TRACKING VEHÍCULO
# ============================================================

def realtime_vehicle_tracking(camera):
    global status_message
    global status_color

    separator()
    print("[TRACKING] SENSOR ACTIVADO")
    print("[TRACKING] YOLO11n + ByteTrack se activarán.")
    print()
    print("ARRIBA -> ABAJO = ENTRY")
    print("ABAJO -> ARRIBA = EXIT")

    show_stage_countdown(
        camera,
        TRACK_PREPARE_SECONDS,
        "TRACKING EN:",
        "Prepara el vehiculo para cruzar la linea",
    )

    reset_tracker()

    track_sides = {}
    detected_event = None
    detected_track_id = None
    detected_vehicle = None
    detected_confidence = 0.0
    start_time = time.time()

    separator()
    print("[TRACKING] ACTIVO ✅")

    while True:
        elapsed = time.time() - start_time

        if elapsed >= TRACK_MAX_SECONDS:
            break

        success, frame = camera.read()
        if not success or frame is None:
            continue

        try:
            results = yolo_model.track(
                source=frame,
                persist=True,
                tracker=TRACKER_CONFIG,
                classes=VEHICLE_CLASSES,
                conf=TRACK_CONFIDENCE,
                verbose=False,
            )
        except Exception as error:
            print("[TRACKING] Error YOLO:")
            print(error)
            return None

        display = frame.copy()
        draw_header(
            display,
            "TRACKING ACTIVO",
            "YOLO11n + ByteTrack | Cruza la linea",
            (0, 255, 0),
        )

        line_y = draw_tracking_line(display)
        remaining = max(0, TRACK_MAX_SECONDS - elapsed)

        cv2.putText(
            display,
            f"Tiempo restante: {remaining:.1f}s",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (255, 255, 255),
            2,
        )

        if results:
            result = results[0]
            boxes = result.boxes

            if boxes is not None and len(boxes) > 0:
                xyxy_list = boxes.xyxy.cpu().numpy()
                cls_list = boxes.cls.int().cpu().tolist()
                conf_list = boxes.conf.cpu().tolist()

                if boxes.id is not None:
                    id_list = boxes.id.int().cpu().tolist()
                else:
                    id_list = [None] * len(xyxy_list)

                for box, class_id, confidence, track_id in zip(
                    xyxy_list,
                    cls_list,
                    conf_list,
                    id_list,
                ):
                    x1, y1, x2, y2 = map(int, box)
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    class_name = yolo_model.names[class_id]

                    cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.circle(display, (center_x, center_y), 7, (0, 0, 255), -1)

                    if track_id is not None:
                        label = f"{class_name} ID:{track_id} {confidence:.0%}"
                    else:
                        label = f"{class_name} {confidence:.0%}"

                    cv2.putText(
                        display,
                        label,
                        (x1, max(25, y1 - 7)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 0),
                        2,
                    )

                    if track_id is None:
                        continue

                    current_side = get_side(center_y, line_y)
                    if current_side is None:
                        continue

                    previous_side = track_sides.get(track_id)

                    if previous_side is None:
                        track_sides[track_id] = current_side
                        continue

                    if previous_side != current_side:
                        if previous_side == "ABOVE" and current_side == "BELOW":
                            detected_event = "ENTRY"
                        elif previous_side == "BELOW" and current_side == "ABOVE":
                            detected_event = "EXIT"

                        if detected_event is not None:
                            detected_track_id = track_id
                            detected_vehicle = class_name
                            detected_confidence = confidence

                            separator()
                            print("✅ CRUCE DETECTADO")
                            print(f"Vehiculo: {class_name}")
                            print(f"Track ID: {track_id}")
                            print(f"Confianza: {confidence:.2%}")
                            print(f"Direccion: {detected_event}")
                            break

                    track_sides[track_id] = current_side

        cv2.imshow(WINDOW_NAME, display)
        cv2.waitKey(1)

        if detected_event is not None:
            show_until = time.time() + 1.2

            while time.time() < show_until:
                success2, frame2 = camera.read()
                if not success2 or frame2 is None:
                    continue

                final_display = frame2.copy()
                draw_header(
                    final_display,
                    f"CRUCE DETECTADO: {detected_event}",
                    f"{detected_vehicle} | ID {detected_track_id} | {detected_confidence:.0%}",
                    (0, 255, 0),
                )
                cv2.imshow(WINDOW_NAME, final_display)
                cv2.waitKey(1)

            return detected_event

    separator()
    print("❌ NO SE DETECTÓ CRUCE DE LA LÍNEA")
    return None


# ============================================================
# DETECTOR FACIAL LOCAL
# ============================================================

def detect_best_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=(90, 90),
    )

    if len(faces) == 0:
        return None

    # Preferir la cara más grande.
    return max(faces, key=lambda item: item[2] * item[3])


# ============================================================
# CAPTURA FACIAL CON CALIDAD + ESTABILIDAD
# ============================================================

def capture_face(camera):
    separator()
    print("PASO 2/4")
    print("DETECCION + CAPTURA AUTOMATICA DE ROSTRO")
    print()
    print(f"[FACE] Tienes {FACE_REPOSITION_SECONDS}s para colocarte frente a la cámara.")
    print("[FACE] Después el sistema esperará una cara centrada, estable y nítida.")

    # Tiempo real para ponerse frente a la cámara.
    show_stage_countdown(
        camera,
        FACE_REPOSITION_SECONDS,
        "PREPARA ROSTRO:",
        "Colocate de frente y mira a la camara",
    )

    print("[FACE] Buscando rostro...")

    started = time.time()
    stable_since = None
    best_frame = None
    best_score = 0.0
    last_good_box = None

    while time.time() - started < FACE_SEARCH_TIMEOUT_SECONDS:
        success, frame = camera.read()
        if not success or frame is None:
            continue

        display = frame.copy()
        box = detect_best_face(frame)
        message = "BUSCANDO ROSTRO..."
        message_color = (0, 255, 255)

        if box is not None:
            x, y, w, h = map(int, box)
            face_crop = crop_with_margin(frame, (x, y, w, h), margin=0.10)
            sharpness = sharpness_score(face_crop)
            width_ratio = w / frame.shape[1]
            centered = box_centered(
                (x, y, w, h),
                frame.shape,
                FACE_CENTER_TOLERANCE_X,
                FACE_CENTER_TOLERANCE_Y,
            )
            size_ok = FACE_MIN_WIDTH_RATIO <= width_ratio <= FACE_MAX_WIDTH_RATIO
            sharp_ok = sharpness >= FACE_MIN_SHARPNESS

            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 3)

            if not size_ok:
                stable_since = None
                best_frame = None
                best_score = 0.0
                message = "ACERCATE UN POCO A LA CAMARA"
                message_color = (0, 165, 255)

            elif not centered:
                stable_since = None
                best_frame = None
                best_score = 0.0
                message = "CENTRA TU ROSTRO Y MIRA AL FRENTE"
                message_color = (0, 165, 255)

            elif not sharp_ok:
                stable_since = None
                best_frame = None
                best_score = 0.0
                message = f"MANTENTE QUIETO | Nitidez {sharpness:.0f}"
                message_color = (0, 165, 255)

            else:
                now = time.time()

                # Si el rostro saltó demasiado entre cuadros, reiniciamos estabilidad.
                if last_good_box is not None:
                    lx, ly, lw, lh = last_good_box
                    center_change = abs((x + w / 2) - (lx + lw / 2)) + abs((y + h / 2) - (ly + lh / 2))
                    max_change = max(w, h) * 0.35
                    if center_change > max_change:
                        stable_since = None
                        best_frame = None
                        best_score = 0.0

                last_good_box = (x, y, w, h)

                if stable_since is None:
                    stable_since = now
                    best_frame = frame.copy()
                    best_score = sharpness

                if sharpness > best_score:
                    best_score = sharpness
                    best_frame = frame.copy()

                stable_elapsed = now - stable_since
                remaining = max(0.0, FACE_STABLE_SECONDS - stable_elapsed)

                message = (
                    f"ROSTRO OK - MIRA A LA CAMARA | "
                    f"mantente {remaining:.1f}s | nitidez {sharpness:.0f}"
                )
                message_color = (0, 255, 0)

                if stable_elapsed >= FACE_STABLE_SECONDS and best_frame is not None:
                    draw_header(
                        display,
                        "ROSTRO LISTO",
                        f"Mejor nitidez: {best_score:.0f} | captura automatica",
                        (0, 255, 0),
                    )
                    cv2.imshow(WINDOW_NAME, display)
                    cv2.waitKey(1)

                    print("[FACE] Rostro estable y bien ubicado ✅")
                    print(f"[FACE] Nitidez seleccionada: {best_score:.0f}")
                    time.sleep(FACE_CONFIRM_SECONDS)
                    return best_frame

        else:
            stable_since = None
            best_frame = None
            best_score = 0.0
            last_good_box = None

        elapsed = time.time() - started
        remaining_search = max(0, FACE_SEARCH_TIMEOUT_SECONDS - elapsed)

        draw_header(
            display,
            message,
            f"Tiempo disponible: {remaining_search:.0f}s",
            message_color,
        )

        cv2.imshow(WINDOW_NAME, display)
        cv2.waitKey(1)

    print("[FACE] Tiempo agotado: no se obtuvo un rostro válido.")
    return None


# ============================================================
# DETECTOR LOCAL DE PLACA
# ============================================================

def detect_plate_with_cascade(frame):
    if not PLATE_CASCADE_AVAILABLE:
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    plates = plate_cascade.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=4,
        minSize=(100, 25),
    )

    if len(plates) == 0:
        return None

    return max(plates, key=lambda item: item[2] * item[3])


def detect_plate_geometric(frame):
    """Fallback geométrico. Devuelve el candidato rectangular más razonable."""
    frame_h, frame_w = frame.shape[:2]

    # Buscar principalmente en la zona central para evitar bordes/objetos laterales.
    x_start = int(frame_w * 0.12)
    x_end = int(frame_w * 0.88)
    y_start = int(frame_h * 0.15)
    y_end = int(frame_h * 0.90)

    roi = frame[y_start:y_end, x_start:x_end]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(gray, 80, 200)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 3))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(
        closed,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    best = None
    best_score = 0.0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if h <= 0:
            continue

        aspect = w / float(h)
        area = w * h
        area_ratio = area / float(roi.shape[0] * roi.shape[1])

        # Matrícula típica: horizontal, no demasiado pequeña ni enorme.
        if not (1.8 <= aspect <= 6.2):
            continue

        if not (0.008 <= area_ratio <= 0.35):
            continue

        rectangularity = area / max(cv2.contourArea(contour), 1.0)
        if rectangularity > 5.0:
            continue

        # Preferir candidatos grandes y cercanos a aspecto ~2.3-3.0.
        aspect_bonus = 1.0 / (1.0 + abs(aspect - 2.7))
        score = area * aspect_bonus

        if score > best_score:
            best_score = score
            best = (x + x_start, y + y_start, w, h)

    return best


def detect_plate_candidate(frame):
    box = detect_plate_with_cascade(frame)
    if box is not None:
        return tuple(map(int, box)), "cascade"

    box = detect_plate_geometric(frame)
    if box is not None:
        return tuple(map(int, box)), "geometry"

    return None, None


# ============================================================
# CAPTURA DE PLACA CON TIEMPO + ESTABILIDAD
# ============================================================

def capture_plate(camera):
    separator()
    print("PASO 3/4")
    print("DETECCION + CAPTURA AUTOMATICA DE PLACA")
    print()
    print(f"[PLATE] Tienes {PLATE_REPOSITION_SECONDS}s para apuntar la cámara a la placa.")
    print("[PLATE] Después espera una matrícula centrada, estable y nítida.")
    print("[PLATE] El frame COMPLETO será enviado al OCR AWS.")

    show_stage_countdown(
        camera,
        PLATE_REPOSITION_SECONDS,
        "PREPARA PLACA:",
        "Apunta a la matricula y acercala al centro",
    )

    print("[PLATE] Buscando placa...")

    started = time.time()
    stable_since = None
    best_frame = None
    best_score = 0.0
    last_good_box = None

    while time.time() - started < PLATE_SEARCH_TIMEOUT_SECONDS:
        success, frame = camera.read()
        if not success or frame is None:
            continue

        display = frame.copy()
        box, detector_name = detect_plate_candidate(frame)
        message = "BUSCANDO PLACA..."
        message_color = (0, 255, 255)

        if box is not None:
            x, y, w, h = box
            crop = crop_with_margin(frame, box, margin=0.08)
            sharpness = sharpness_score(crop)
            width_ratio = w / frame.shape[1]
            centered = box_centered(
                box,
                frame.shape,
                PLATE_CENTER_TOLERANCE_X,
                PLATE_CENTER_TOLERANCE_Y,
            )
            size_ok = PLATE_MIN_WIDTH_RATIO <= width_ratio <= PLATE_MAX_WIDTH_RATIO
            sharp_ok = sharpness >= PLATE_MIN_SHARPNESS

            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 3)

            if not size_ok:
                stable_since = None
                best_frame = None
                best_score = 0.0
                message = "ACERCA LA PLACA UN POCO MAS"
                message_color = (0, 165, 255)

            elif not centered:
                stable_since = None
                best_frame = None
                best_score = 0.0
                message = "CENTRA LA PLACA EN LA CAMARA"
                message_color = (0, 165, 255)

            elif not sharp_ok:
                stable_since = None
                best_frame = None
                best_score = 0.0
                message = f"ENFOCA Y MANTEN ESTABLE | Nitidez {sharpness:.0f}"
                message_color = (0, 165, 255)

            else:
                now = time.time()

                if last_good_box is not None:
                    lx, ly, lw, lh = last_good_box
                    center_change = abs((x + w / 2) - (lx + lw / 2)) + abs((y + h / 2) - (ly + lh / 2))
                    max_change = max(w, h) * 0.40

                    if center_change > max_change:
                        stable_since = None
                        best_frame = None
                        best_score = 0.0

                last_good_box = box

                if stable_since is None:
                    stable_since = now
                    best_frame = frame.copy()
                    best_score = sharpness

                if sharpness > best_score:
                    best_score = sharpness
                    best_frame = frame.copy()

                stable_elapsed = now - stable_since
                remaining = max(0.0, PLATE_STABLE_SECONDS - stable_elapsed)

                message = (
                    f"PLACA OK ({detector_name}) - mantenla {remaining:.1f}s "
                    f"| nitidez {sharpness:.0f}"
                )
                message_color = (0, 255, 0)

                if stable_elapsed >= PLATE_STABLE_SECONDS and best_frame is not None:
                    draw_header(
                        display,
                        "PLACA LISTA",
                        f"Mejor nitidez: {best_score:.0f} | captura automatica",
                        (0, 255, 0),
                    )
                    cv2.imshow(WINDOW_NAME, display)
                    cv2.waitKey(1)

                    print("[PLATE] Placa estable y bien ubicada ✅")
                    print(f"[PLATE] Nitidez seleccionada: {best_score:.0f}")
                    print("[PLATE] Se enviará el frame completo al OCR para evitar un recorte incorrecto.")
                    time.sleep(PLATE_CONFIRM_SECONDS)
                    return best_frame

        else:
            stable_since = None
            best_frame = None
            best_score = 0.0
            last_good_box = None

        elapsed = time.time() - started
        remaining_search = max(0, PLATE_SEARCH_TIMEOUT_SECONDS - elapsed)

        draw_header(
            display,
            message,
            f"Tiempo disponible: {remaining_search:.0f}s",
            message_color,
        )

        cv2.imshow(WINDOW_NAME, display)
        cv2.waitKey(1)

    print("[PLATE] Tiempo agotado: no se obtuvo una placa válida.")
    return None


# ============================================================
# BACKEND 1.6
# ============================================================

def process_access(face_frame, plate_frame, event_type):
    global status_message
    global status_color

    separator()
    print("PASO 4/4")
    print("AUTORIZACION MEDIANTE BACKEND 1.6")
    separator()

    print("[CLOUD] Procesando acceso mediante Backend 1.6...")
    print(f"[CLOUD] Evento ByteTrack: {event_type}")
    print(f"[CLOUD] POST {PROCESS_URL}")
    print()
    print("[CLOUD] Backend -> IA 2.7 -> ArcFace + RetinaFace")
    print("[CLOUD] Backend -> IA 2.7 -> OCR 1.1")
    print("[CLOUD] IA -> Backend -> autorización")
    print("[CLOUD] Backend -> RDS + AWS IoT")

    try:
        face_bytes = frame_to_jpeg(face_frame)
        plate_bytes = frame_to_jpeg(plate_frame)

        start_time = time.time()

        response = httpx.post(
            PROCESS_URL,
            files={
                "face_image": ("face.jpg", face_bytes, "image/jpeg"),
                "plate_image": ("plate.jpg", plate_bytes, "image/jpeg"),
            },
            data={"event_type": event_type},
            timeout=180.0,
        )

        elapsed = time.time() - start_time

        if not response.is_success:
            separator()
            print("[CLOUD] BACKEND RESPONDIÓ CON ERROR:")
            print(f"HTTP {response.status_code}")
            try:
                print(response.json())
            except Exception:
                print(response.text)
            return None

        result = response.json()

        person = result.get("person") or "No identificado"
        face_recognized = bool(result.get("face_recognized", False))
        face_score = float(result.get("face_score", 0.0) or 0.0)
        plate = result.get("plate_display") or result.get("detected_plate") or "No detectada"
        plate_score = float(result.get("plate_score", 0.0) or 0.0)
        authorization_called = bool(result.get("authorization_called", False))
        authorization = result.get("authorization") or {}
        decision = authorization.get("decision") or result.get("decision")
        reason = authorization.get("reason") or result.get("reason")
        user_id = authorization.get("user_id") or result.get("user_id")
        vehicle_id = authorization.get("vehicle_id") or result.get("vehicle_id")

        separator()
        print("SMARTPARK UCE - RESULTADO FINAL")
        separator()
        print(f"Movimiento:            {event_type}")
        print()
        print(f"Persona:               {person}")
        print(f"Rostro reconocido:     {face_recognized}")
        print(f"Confianza rostro:      {face_score:.2%}")
        print()
        print(f"Placa:                 {plate}")
        print(f"Confianza placa:       {plate_score:.2%}")
        print()
        print(f"Backend ejecutado:     {authorization_called}")
        print(f"User ID:               {user_id}")
        print(f"Vehicle ID:            {vehicle_id}")
        print()
        print(f"Decision:              {decision}")
        print(f"Razon:                 {reason}")
        print()
        print(f"Tiempo cloud:          {elapsed:.2f}s")
        separator()

        if decision == "AUTHORIZED":
            print("✅ ACCESO AUTORIZADO")
            status_message = f"AUTHORIZED | {event_type} | {plate}"
            status_color = (0, 255, 0)

        elif decision in ("DENIED", "REJECTED"):
            print("❌ ACCESO RECHAZADO")
            status_message = f"DENIED | {plate}"
            status_color = (0, 0, 255)

        else:
            print("⚠ SIN DECISION")
            status_message = "SIN DECISION"
            status_color = (0, 165, 255)

        return {
            "decision": decision,
            "person": person,
            "plate": plate,
            "face_score": face_score,
            "plate_score": plate_score,
            "reason": reason,
        }

    except Exception as error:
        separator()
        print("[CLOUD] ERROR:")
        print(error)
        status_message = "ERROR CLOUD"
        status_color = (0, 0, 255)
        return None


# ============================================================
# RESULTADO FINAL EN VENTANA
# ============================================================

def show_final_result(camera, event_type, result):
    if result is None:
        return

    decision = result.get("decision")
    person = result.get("person")
    plate = result.get("plate")
    face_score = float(result.get("face_score", 0.0) or 0.0)
    plate_score = float(result.get("plate_score", 0.0) or 0.0)

    start = time.time()

    while time.time() - start < FINAL_RESULT_SECONDS:
        success, frame = camera.read()
        if not success or frame is None:
            continue

        display = frame.copy()

        if decision == "AUTHORIZED":
            title = "ACCESO AUTORIZADO"
            color = (0, 255, 0)
        else:
            title = "ACCESO RECHAZADO"
            color = (0, 0, 255)

        draw_header(display, title, f"Movimiento: {event_type}", color)

        cv2.putText(
            display,
            f"Persona: {person}",
            (30, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            color,
            2,
        )

        cv2.putText(
            display,
            f"Rostro: {face_score:.2%}",
            (30, 225),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2,
        )

        cv2.putText(
            display,
            f"Placa: {plate}",
            (30, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            color,
            2,
        )

        cv2.putText(
            display,
            f"OCR: {plate_score:.2%}",
            (30, 325),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2,
        )

        cv2.imshow(WINDOW_NAME, display)
        cv2.waitKey(1)


# ============================================================
# CICLO AUTOMÁTICO COMPLETO
# ============================================================

def automatic_access_cycle(camera):
    global processing
    global status_message
    global status_color

    processing = True

    try:
        separator()
        print("🚗 HC-SR04 ACTIVÓ SMARTPARK")

        # PASO 1: vehículo / ENTRY-EXIT
        status_message = "TRACKING ACTIVO"
        status_color = (0, 255, 0)

        event_type = realtime_vehicle_tracking(camera)

        if event_type is None:
            status_message = "NO SE DETECTO ENTRY / EXIT"
            status_color = (0, 0, 255)
            return

        # PASO 2: rostro
        face_frame = capture_face(camera)

        if face_frame is None:
            print("[FACE] No se obtuvo una captura válida. Ciclo cancelado.")
            status_message = "ROSTRO NO DETECTADO"
            status_color = (0, 0, 255)
            return

        # PASO 3: placa
        plate_frame = capture_plate(camera)

        if plate_frame is None:
            print("[PLATE] No se obtuvo una captura válida. Ciclo cancelado.")
            status_message = "PLACA NO DETECTADA"
            status_color = (0, 0, 255)
            return

        # PASO 4: cloud
        result = process_access(face_frame, plate_frame, event_type)
        show_final_result(camera, event_type, result)

    finally:
        processing = False
        vehicle_event.clear()
        status_message = "ESPERANDO SIGUIENTE VEHICULO..."
        status_color = (255, 255, 255)

        separator()
        print("[SMARTPARK] CICLO TERMINADO")
        print("[SMARTPARK] Esperando siguiente vehículo...")


# ============================================================
# MAIN
# ============================================================

def main():
    separator()
    print("SMARTPARK UCE")
    print("GARITA AUTOMATICA - SENSOR + TRACKING + BIOMETRIA + OCR")
    separator()

    if not check_cloud():
        return

    camera = open_camera()
    if camera is None:
        return

    try:
        connect_mqtt()
    except Exception as error:
        print("[AWS IOT] ERROR:")
        print(error)
        camera.release()
        return

    separator()
    print("✅ SISTEMA LISTO")
    print("La cámara está encendida.")
    print("YOLO y ByteTrack esperan al HC-SR04.")
    print(f"Rostro: {FACE_REPOSITION_SECONDS}s para posicionarse + {FACE_STABLE_SECONDS:.1f}s estable.")
    print(f"Placa:  {PLATE_REPOSITION_SECONDS}s para apuntar + {PLATE_STABLE_SECONDS:.1f}s estable.")
    separator()

    try:
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                continue

            if not processing and not vehicle_event.is_set():
                display = frame.copy()
                draw_header(
                    display,
                    "ESPERANDO VEHICULO...",
                    "HC-SR04 + AWS IoT conectados",
                    (255, 255, 255),
                )

                if last_distance is not None:
                    cv2.putText(
                        display,
                        f"Ultima deteccion: {last_distance} cm",
                        (20, 155),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.50,
                        (255, 255, 255),
                        1,
                    )

                cv2.putText(
                    display,
                    "Q = salir",
                    (20, display.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (255, 255, 255),
                    1,
                )

                cv2.imshow(WINDOW_NAME, display)

            if vehicle_event.is_set() and not processing:
                vehicle_event.clear()
                automatic_access_cycle(camera)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q")):
                break

    except KeyboardInterrupt:
        pass

    camera.release()
    cv2.destroyAllWindows()

    if mqtt_connection is not None:
        try:
            mqtt_connection.disconnect().result()
        except Exception:
            pass

    separator()
    print("[SMARTPARK] Sistema cerrado.")


if __name__ == "__main__":
    main()
