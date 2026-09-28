import os

from ultralytics import YOLO


# ============================================================
# CONFIGURACION
# ============================================================

MODEL_PATH = "/app/yolo11n.pt"

TRACKER_PATH = (
    "/app/ai/bytetrack_smartpark.yaml"
)

VEHICLE_CLASSES = [
    2,  # car
    3,  # motorcycle
    5,  # bus
    7,  # truck
]

CONFIDENCE = 0.35

IOU_THRESHOLD = 0.50


# ============================================================
# MODELO
# ============================================================

print("[TRACKING] Cargando YOLO11n + ByteTrack...")

tracking_model = YOLO(
    MODEL_PATH
)

print("[TRACKING] Modelo listo.")


# ============================================================
# TRACK VIDEO
# ============================================================

def track_vehicle_video(
    video_path: str
):

    if not os.path.exists(
        video_path
    ):

        return {
            "status": "error",
            "detail": "Video not found"
        }


    # Guarda última posición vertical
    # de cada track_id.
    previous_centers = {}


    # Eventos encontrados
    events = []


    # IDs que ya generaron evento
    processed_tracks = set()


    results = tracking_model.track(

        source=video_path,

        stream=True,

        persist=True,

        tracker=TRACKER_PATH,

        classes=VEHICLE_CLASSES,

        conf=CONFIDENCE,

        iou=IOU_THRESHOLD,

        verbose=False,
    )


    frame_number = 0


    for result in results:

        frame_number += 1


        if result.boxes is None:
            continue


        # Necesitamos IDs de ByteTrack
        if result.boxes.id is None:
            continue


        frame_height = (
            result.orig_shape[0]
        )


        # Línea virtual al centro
        line_y = int(
            frame_height * 0.50
        )


        boxes = (
            result.boxes.xyxy
            .cpu()
            .numpy()
        )

        ids = (
            result.boxes.id
            .int()
            .cpu()
            .tolist()
        )

        classes = (
            result.boxes.cls
            .int()
            .cpu()
            .tolist()
        )

        confidences = (
            result.boxes.conf
            .cpu()
            .tolist()
        )


        for (
            box,
            track_id,
            class_id,
            confidence
        ) in zip(
            boxes,
            ids,
            classes,
            confidences
        ):

            x1, y1, x2, y2 = box


            center_y = int(
                (y1 + y2) / 2
            )


            previous_y = (
                previous_centers.get(
                    track_id
                )
            )


            # --------------------------------------------
            # Ya teníamos posición previa.
            # Revisamos si cruzó la línea.
            # --------------------------------------------

            if (
                previous_y is not None
                and
                track_id
                not in processed_tracks
            ):

                # Arriba -> abajo
                if (
                    previous_y < line_y
                    and
                    center_y >= line_y
                ):

                    events.append(
                        {
                            "track_id":
                                track_id,

                            "event_type":
                                "ENTRY",

                            "class_id":
                                class_id,

                            "confidence":
                                float(
                                    confidence
                                ),

                            "frame":
                                frame_number,
                        }
                    )


                    processed_tracks.add(
                        track_id
                    )


                # Abajo -> arriba
                elif (
                    previous_y > line_y
                    and
                    center_y <= line_y
                ):

                    events.append(
                        {
                            "track_id":
                                track_id,

                            "event_type":
                                "EXIT",

                            "class_id":
                                class_id,

                            "confidence":
                                float(
                                    confidence
                                ),

                            "frame":
                                frame_number,
                        }
                    )


                    processed_tracks.add(
                        track_id
                    )


            previous_centers[
                track_id
            ] = center_y


    # ========================================================
    # RESPUESTA
    # ========================================================

    if not events:

        return {
            "status": "ok",
            "vehicle_tracked": True,
            "crossing_detected": False,
            "event_type": None
        }


    # Para el prototipo tomamos
    # el primer cruce detectado.
    event = events[0]


    return {
        "status": "ok",
        "vehicle_tracked": True,
        "crossing_detected": True,
        "event_type":
            event["event_type"],
        "track_id":
            event["track_id"],
        "confidence":
            event["confidence"]
    }