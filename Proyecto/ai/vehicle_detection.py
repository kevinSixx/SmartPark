import time
from pathlib import Path

import cv2
from ultralytics import YOLO


# =========================================================
# IMPORTAR RECONOCIMIENTO FACIAL
# =========================================================

try:
    from ai.face_recognition import recognize_face

except ModuleNotFoundError:
    from face_recognition import recognize_face


# =========================================================
# RUTAS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

MODEL_PATH = (
    PROJECT_ROOT
    / "yolo11n.pt"
)

TRACKER_PATH = (
    Path(__file__)
    .resolve()
    .parent
    / "bytetrack_smartpark.yaml"
)


# =========================================================
# CÁMARA
# =========================================================

# DroidCam virtual de Windows.
CAMERA_INDEX = 0

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720


# =========================================================
# YOLO
# =========================================================

VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


# Bajamos la confianza porque estamos usando
# carros pequeños/de juguete.
CONFIDENCE = 0.15

# Imagen más grande para ayudar a detectar
# objetos pequeños.
YOLO_IMAGE_SIZE = 960

# IoU para eliminar cajas duplicadas.
IOU_THRESHOLD = 0.50


# =========================================================
# ENTRY / EXIT
# =========================================================

LINE_POSITION = 0.50

# Zona neutra alrededor de la línea.
LINE_MARGIN = 25

# Frames consecutivos para confirmar el nuevo lado.
STABLE_FRAMES = 4

# Evita múltiples eventos del mismo vehículo
# en un intervalo muy corto.
EVENT_COOLDOWN = 3.0

# Mostrar resultados unos segundos.
EVENT_DISPLAY_TIME = 4.0


# =========================================================
# MODELO
# =========================================================

print("[YOLO] Cargando modelo...")

model = YOLO(
    str(MODEL_PATH)
)

print("[YOLO] Modelo cargado.")


# =========================================================
# ESTADO
# =========================================================

vehicle_states = {}

last_event_message = ""
last_event_display_time = 0.0

last_face_result = None
last_face_display_time = 0.0


# =========================================================
# ENTRY / EXIT
# =========================================================

def get_side(
    center_y: int,
    line_y: int
) -> int:
    """
    -1 = arriba de la línea
     0 = zona neutra
     1 = debajo de la línea
    """

    if center_y < line_y - LINE_MARGIN:
        return -1

    if center_y > line_y + LINE_MARGIN:
        return 1

    return 0


def register_side(
    track_id: int,
    current_side: int
):
    """
    Determina si el vehículo cruzó realmente
    la línea de acceso.
    """

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

    # ---------------------------------------------
    # NUEVO LADO CANDIDATO
    # ---------------------------------------------

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


    # ---------------------------------------------
    # ESPERAMOS ESTABILIDAD
    # ---------------------------------------------

    if (
        state["candidate_frames"]
        < STABLE_FRAMES
    ):
        return None


    previous_side = state[
        "stable_side"
    ]


    # Primera posición conocida.
    if previous_side is None:

        state["stable_side"] = (
            current_side
        )

        return None


    # Sigue en el mismo lado.
    if previous_side == current_side:
        return None


    # ---------------------------------------------
    # CRUCE CONFIRMADO
    # ---------------------------------------------

    state["stable_side"] = (
        current_side
    )

    now = time.monotonic()


    if (
        now
        - state["last_event_time"]
        < EVENT_COOLDOWN
    ):
        return None


    state["last_event_time"] = now


    if (
        previous_side == -1
        and
        current_side == 1
    ):
        return "ENTRY"


    if (
        previous_side == 1
        and
        current_side == -1
    ):
        return "EXIT"


    return None


# =========================================================
# DIBUJAR RESULTADO FACIAL
# =========================================================

def draw_face_result(
    frame,
    result
):

    area = result.get(
        "facial_area"
    )

    if not area:
        return


    x = int(
        area.get("x", 0)
    )

    y = int(
        area.get("y", 0)
    )

    w = int(
        area.get("w", 0)
    )

    h = int(
        area.get("h", 0)
    )


    recognized = result.get(
        "recognized",
        False
    )


    if recognized:

        color = (
            0,
            255,
            0
        )

    else:

        color = (
            0,
            0,
            255
        )


    cv2.rectangle(
        frame,
        (x, y),
        (
            x + w,
            y + h
        ),
        color,
        3
    )


    name = result.get(
        "name",
        "DESCONOCIDO"
    )

    similarity = result.get(
        "similarity",
        0.0
    )


    label = (
        f"{name} "
        f"{similarity * 100:.1f}%"
    )


    cv2.putText(
        frame,
        label,
        (
            x,
            max(
                y - 15,
                30
            )
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        color,
        2
    )


# =========================================================
# MAIN
# =========================================================

def main():

    global last_event_message
    global last_event_display_time

    global last_face_result
    global last_face_display_time


    print()
    print(
        "=========================================="
    )

    print(
        " SMARTPARK UCE - DETECCION DE VEHICULOS"
    )

    print(
        "=========================================="
    )

    print()


    # =====================================================
    # ABRIR CÁMARA
    # =====================================================

    print(
        "[CAMERA] Abriendo DroidCam..."
    )


    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )


    if not camera.isOpened():

        print(
            f"[CAMERA] No se pudo abrir "
            f"el índice {CAMERA_INDEX}."
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


    actual_width = int(
        camera.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    actual_height = int(
        camera.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )


    print(
        f"[CAMERA] Cámara iniciada: "
        f"{actual_width}x{actual_height}"
    )


    print(
        f"[YOLO] Confianza mínima: "
        f"{CONFIDENCE}"
    )

    print(
        f"[YOLO] Tamaño de inferencia: "
        f"{YOLO_IMAGE_SIZE}"
    )

    print(
        "[TRACKING] ByteTrack SmartPark activo."
    )

    print(
        "[FACE] Reconocimiento facial listo."
    )

    print(
        "[SMARTPARK] Presiona Q para salir."
    )


    # =====================================================
    # LOOP
    # =====================================================

    while True:

        success, frame = camera.read()


        if not success:

            print(
                "[CAMERA] No se pudo leer el frame."
            )

            break


        height, width = (
            frame.shape[:2]
        )


        line_y = int(
            height
            * LINE_POSITION
        )


        # =================================================
        # LÍNEA DE ACCESO
        # =================================================

        cv2.line(
            frame,
            (
                0,
                line_y
            ),
            (
                width,
                line_y
            ),
            (
                255,
                0,
                0
            ),
            3
        )


        # Margen superior.
        cv2.line(
            frame,
            (
                0,
                line_y - LINE_MARGIN
            ),
            (
                width,
                line_y - LINE_MARGIN
            ),
            (
                150,
                150,
                150
            ),
            1
        )


        # Margen inferior.
        cv2.line(
            frame,
            (
                0,
                line_y + LINE_MARGIN
            ),
            (
                width,
                line_y + LINE_MARGIN
            ),
            (
                150,
                150,
                150
            ),
            1
        )


        cv2.putText(
            frame,
            "LINEA DE ACCESO",
            (
                20,
                max(
                    line_y - 15,
                    30
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (
                255,
                0,
                0
            ),
            2
        )


        # =================================================
        # YOLO + BYTETRACK MEJORADO
        # =================================================

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


        # =================================================
        # RESULTADOS
        # =================================================

        for result in results:

            if result.boxes is None:
                continue


            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )


                if (
                    class_id
                    not in VEHICLE_CLASSES
                ):
                    continue


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


                # -----------------------------------------
                # TRACK ID
                # -----------------------------------------

                if box.id is None:

                    track_id = None

                else:

                    track_id = int(
                        box.id[0]
                    )


                center_x = int(
                    (
                        x1 + x2
                    )
                    / 2
                )

                center_y = int(
                    (
                        y1 + y2
                    )
                    / 2
                )


                # =================================================
                # ENTRY / EXIT
                # =================================================

                event_type = None


                if track_id is not None:

                    current_side = get_side(
                        center_y,
                        line_y
                    )


                    event_type = register_side(
                        track_id,
                        current_side
                    )


                # =================================================
                # EVENTO DETECTADO
                # =================================================

                if event_type:

                    print()
                    print(
                        "--------------------------------------"
                    )


                    print(
                        f"[VEHICLE] "
                        f"ID:{track_id} "
                        f"{event_type}"
                    )


                    print(
                        f"[VEHICLE] Clase: "
                        f"{VEHICLE_CLASSES[class_id]}"
                    )


                    print(
                        f"[VEHICLE] Confianza: "
                        f"{confidence * 100:.1f}%"
                    )


                    last_event_message = (
                        f"{event_type} - "
                        f"Vehicle ID:{track_id}"
                    )


                    last_event_display_time = (
                        time.monotonic()
                    )


                    # =================================================
                    # RECONOCIMIENTO FACIAL AUTOMÁTICO
                    # =================================================

                    print(
                        "[FACE] Analizando rostro..."
                    )


                    face_result = recognize_face(
                        frame.copy()
                    )


                    last_face_result = (
                        face_result
                    )


                    last_face_display_time = (
                        time.monotonic()
                    )


                    face_name = (
                        face_result.get(
                            "name",
                            "SIN ROSTRO"
                        )
                    )


                    face_similarity = (
                        face_result.get(
                            "similarity",
                            0.0
                        )
                    )


                    print(
                        f"[FACE] Resultado: "
                        f"{face_name}"
                    )


                    print(
                        f"[FACE] Similitud: "
                        f"{face_similarity * 100:.2f}%"
                    )


                    print(
                        "--------------------------------------"
                    )


                # =================================================
                # DIBUJAR VEHÍCULO
                # =================================================

                if track_id is None:

                    id_text = "ID:?"

                else:

                    id_text = (
                        f"ID:{track_id}"
                    )


                label = (
                    f"{VEHICLE_CLASSES[class_id]} "
                    f"{id_text} "
                    f"{confidence:.2f}"
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


                cv2.circle(
                    frame,
                    (
                        center_x,
                        center_y
                    ),
                    6,
                    (
                        0,
                        0,
                        255
                    ),
                    -1
                )


                cv2.putText(
                    frame,
                    label,
                    (
                        x1,
                        max(
                            y1 - 10,
                            25
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


        # =================================================
        # MOSTRAR ÚLTIMO EVENTO
        # =================================================

        if (
            last_event_message
            and
            time.monotonic()
            - last_event_display_time
            < EVENT_DISPLAY_TIME
        ):

            cv2.putText(
                frame,
                last_event_message,
                (
                    30,
                    50
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (
                    0,
                    0,
                    255
                ),
                3
            )


        # =================================================
        # MOSTRAR RESULTADO FACIAL
        # =================================================

        if (
            last_face_result
            and
            time.monotonic()
            - last_face_display_time
            < EVENT_DISPLAY_TIME
        ):

            draw_face_result(
                frame,
                last_face_result
            )


            face_name = (
                last_face_result.get(
                    "name",
                    ""
                )
            )


            cv2.putText(
                frame,
                f"ROSTRO: {face_name}",
                (
                    30,
                    90
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (
                    255,
                    255,
                    255
                ),
                2
            )


        # =================================================
        # INFORMACIÓN DEL SISTEMA
        # =================================================

        cv2.putText(
            frame,
            "SmartPark UCE",
            (
                width - 210,
                35
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (
                255,
                255,
                255
            ),
            2
        )


        cv2.putText(
            frame,
            "YOLO11n + ByteTrack",
            (
                width - 250,
                65
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                255,
                255,
                255
            ),
            1
        )


        # =================================================
        # MOSTRAR VENTANA
        # =================================================

        cv2.imshow(
            "SmartPark UCE - Control Inteligente",
            frame
        )


        if (
            cv2.waitKey(1)
            & 0xFF
            == ord("q")
        ):

            break


    # =====================================================
    # CERRAR
    # =====================================================

    camera.release()

    cv2.destroyAllWindows()


    print()
    print(
        "[SMARTPARK] Sistema detenido."
    )


if __name__ == "__main__":
    main()