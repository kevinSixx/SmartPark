import os

import asyncio

import tempfile

import time



import cv2

import httpx

import numpy as np



from deepface import DeepFace



from fastapi import (

    FastAPI,

    File,

    Form,

    HTTPException,

    UploadFile,

)


from starlette.concurrency import run_in_threadpool



from ai.face_recognition import recognize_face



from ai.vehicle_detection import (

    model,

    VEHICLE_CLASSES,

    CONFIDENCE,

    YOLO_IMAGE_SIZE,

    IOU_THRESHOLD,

)





# ============================================================

# SMARTPARK AI 2.8

#

# - YOLO11n

# - ByteTrack

# - RetinaFace

# - ArcFace / DeepFace

# - Enrolamiento facial 3-5 fotos

# - Reconocimiento dinamico contra Backend/RDS

# - OCR externo smartpark_ocr

# - Autorizacion Backend

# ============================================================





# ============================================================

# CONFIGURACION

# ============================================================



OCR_SERVICE_URL = os.getenv(

    "OCR_SERVICE_URL",

    "http://smartpark_ocr:8002/plate"

)



BACKEND_AUTHORIZE_URL = os.getenv(

    "BACKEND_AUTHORIZE_URL",

    "http://smartpark-backend-alb-1439743232.us-east-1.elb.amazonaws.com/api/v1/access/authorize"

)



BACKEND_FACE_MATCH_URL = os.getenv(

    "BACKEND_FACE_MATCH_URL",

    "http://smartpark-backend-alb-1439743232.us-east-1.elb.amazonaws.com/api/v1/face-profiles/match"

)



TRACKER_PATH = os.getenv(

    "TRACKER_PATH",

    "/app/ai/bytetrack_smartpark.yaml"

)



FACE_MODEL_NAME = os.getenv(

    "FACE_MODEL_NAME",

    "ArcFace"

)



FACE_DETECTOR_BACKEND = os.getenv(

    "FACE_DETECTOR_BACKEND",

    "retinaface"

)



MIN_ENROLLMENT_IMAGES = 3

MAX_ENROLLMENT_IMAGES = 5


# Estado de preparacion de los modelos faciales.
FACE_MODELS_READY = False

FACE_WARMUP_SECONDS = None

FACE_WARMUP_ERROR = None

# DeepFace / TensorFlow se ejecuta fuera del event loop y se serializa
# por proceso para evitar inferencias faciales simultaneas sobre los
# mismos modelos.
FACE_INFERENCE_LOCK = asyncio.Lock()





# ============================================================

# FASTAPI

# ============================================================



app = FastAPI(

    title="SmartPark AI Service",

    version="2.8.1"

)





# ============================================================

# UTILIDAD - DECODIFICAR IMAGEN

# ============================================================



def decode_image(contents: bytes):



    np_array = np.frombuffer(

        contents,

        np.uint8

    )



    frame = cv2.imdecode(

        np_array,

        cv2.IMREAD_COLOR

    )



    if frame is None:

        raise HTTPException(

            status_code=400,

            detail="Imagen invalida"

        )



    return frame





# ============================================================

# UTILIDAD - NORMALIZAR EMBEDDING

# ============================================================



def normalize_embedding(

    embedding: list[float]

) -> list[float]:



    vector = np.asarray(

        embedding,

        dtype=np.float32

    )



    norm = float(

        np.linalg.norm(vector)

    )



    if norm <= 0.0:

        raise HTTPException(

            status_code=500,

            detail="Embedding facial invalido"

        )



    vector = vector / norm



    return [

        float(value)

        for value in vector.tolist()

    ]





# ============================================================

# UTILIDAD - EXTRAER UN SOLO ROSTRO / EMBEDDING

# ============================================================



def extract_single_face_embedding(

    frame

) -> dict:



    try:

        representations = DeepFace.represent(

            img_path=frame,

            model_name=FACE_MODEL_NAME,

            detector_backend=FACE_DETECTOR_BACKEND,

            enforce_detection=True,

            align=True

        )



    except Exception as error:

        raise HTTPException(

            status_code=422,

            detail=(

                "No se pudo detectar/procesar "

                f"el rostro: {error}"

            )

        ) from error



    if not representations:

        raise HTTPException(

            status_code=422,

            detail="No se detecto ningun rostro"

        )



    if len(representations) != 1:

        raise HTTPException(

            status_code=422,

            detail=(

                "Cada imagen debe contener "

                "exactamente un rostro"

            )

        )



    face_data = representations[0]



    raw_embedding = face_data.get(

        "embedding"

    )



    if (

        not isinstance(raw_embedding, list)

        or

        not raw_embedding

    ):

        raise HTTPException(

            status_code=500,

            detail=(

                "DeepFace no devolvio "

                "un embedding valido"

            )

        )



    embedding = normalize_embedding(

        raw_embedding

    )



    facial_area = (

        face_data.get(

            "facial_area"

        )

        or

        {}

    )



    face_confidence = face_data.get(

        "face_confidence"

    )



    if face_confidence is None:

        face_confidence = face_data.get(

            "confidence"

        )



    if face_confidence is None:

        face_confidence = 1.0



    try:

        face_confidence = float(

            face_confidence

        )

    except Exception:

        face_confidence = 1.0



    face_confidence = max(

        0.0,

        min(

            1.0,

            face_confidence

        )

    )



    return {

        "embedding":

            embedding,



        "embedding_dimension":

            len(embedding),



        "quality_score":

            face_confidence,



        "facial_area":

            facial_area

    }





# ============================================================

# WARM-UP FACIAL / READINESS

# ============================================================


def warmup_face_models():

    global FACE_MODELS_READY
    global FACE_WARMUP_SECONDS
    global FACE_WARMUP_ERROR

    FACE_MODELS_READY = False
    FACE_WARMUP_ERROR = None

    print(
        "[FACE] Iniciando warm-up "
        "RetinaFace + ArcFace..."
    )

    started_at = time.perf_counter()

    try:

        # Imagen artificial. Su unico objetivo es forzar a DeepFace
        # a inicializar RetinaFace y ArcFace antes del primer acceso.
        dummy_frame = np.full(
            (224, 224, 3),
            127,
            dtype=np.uint8
        )

        DeepFace.represent(
            img_path=dummy_frame,
            model_name=FACE_MODEL_NAME,
            detector_backend=FACE_DETECTOR_BACKEND,
            enforce_detection=False,
            align=True
        )

        FACE_MODELS_READY = True

    except Exception as error:

        FACE_WARMUP_ERROR = (
            f"{type(error).__name__}: {error}"
        )

        print(
            "[FACE] Error durante warm-up: "
            f"{FACE_WARMUP_ERROR}"
        )

    finally:

        FACE_WARMUP_SECONDS = (
            time.perf_counter()
            -
            started_at
        )

    if FACE_MODELS_READY:

        print(
            "[FACE] Warm-up completado. "
            "RetinaFace + ArcFace listos. "
            f"Tiempo: {FACE_WARMUP_SECONDS:.2f}s"
        )


@app.on_event("startup")
async def startup_warmup_face_models():

    # FastAPI no termina el startup hasta finalizar este warm-up.
    # Asi una instancia nueva no recibe su primer vehiculo con los
    # modelos todavia frios.
    await run_in_threadpool(
        warmup_face_models
    )


# ============================================================

# UTILIDAD - BACKEND MATCH FACIAL

# ============================================================



async def match_embedding_with_backend(

    embedding: list[float]

) -> dict:



    try:

        async with httpx.AsyncClient(

            timeout=30.0

        ) as client:



            response = await client.post(

                BACKEND_FACE_MATCH_URL,

                json={

                    "embedding":

                        embedding

                }

            )



            response.raise_for_status()



            return response.json()



    except httpx.RequestError as error:

        raise HTTPException(

            status_code=503,

            detail=(

                "No se pudo conectar con "

                "el backend para comparar "

                f"el rostro: {error}"

            )

        ) from error



    except httpx.HTTPStatusError as error:

        raise HTTPException(

            status_code=502,

            detail=(

                "El backend de reconocimiento "

                "facial respondio con error "

                f"{error.response.status_code}: "

                f"{error.response.text}"

            )

        ) from error





# ============================================================

# UTILIDAD - RECONOCIMIENTO FACIAL DINAMICO

# ============================================================



async def recognize_face_dynamic(

    frame

) -> dict:



    total_started_at = time.perf_counter()

    embedding_started_at = time.perf_counter()

    async with FACE_INFERENCE_LOCK:

        face_data = await run_in_threadpool(

            extract_single_face_embedding,

            frame

        )

    embedding_seconds = (
        time.perf_counter()
        -
        embedding_started_at
    )

    print(
        "[FACE] Embedding generado en "
        f"{embedding_seconds:.2f}s"
    )



    match_started_at = time.perf_counter()

    match_result = await match_embedding_with_backend(

        face_data[

            "embedding"

        ]

    )

    match_seconds = (
        time.perf_counter()
        -
        match_started_at
    )

    print(
        "[FACE] Match Backend/RDS en "
        f"{match_seconds:.2f}s"
    )

    print(
        "[FACE] Reconocimiento dinamico total en "
        f"{time.perf_counter() - total_started_at:.2f}s"
    )



    matched = bool(

        match_result.get(

            "matched",

            False

        )

    )



    similarity = float(

        match_result.get(

            "similarity",

            0.0

        )

        or

        0.0

    )



    return {

        "recognized":

            matched,



        "name":

            match_result.get(

                "person"

            ),



        "user_id":

            match_result.get(

                "user_id"

            ),



        "institutional_id":

            match_result.get(

                "institutional_id"

            ),



        "similarity":

            similarity,



        "threshold":

            match_result.get(

                "threshold"

            ),



        "model_name":

            FACE_MODEL_NAME,



        "detector_backend":

            FACE_DETECTOR_BACKEND,



        "embedding_dimension":

            face_data[

                "embedding_dimension"

            ],



        "quality_score":

            face_data[

                "quality_score"

            ]

    }





# ============================================================

# HEALTH

# ============================================================



@app.get("/health")

def health():



    return {

        "status":

            "ok",



        "service":

            "smartpark-ai",



        "version":

            "2.8.1",



        "yolo":

            "YOLO11n",



        "tracker":

            "ByteTrack",



        "face_model":

            FACE_MODEL_NAME,



        "face_detector":

            FACE_DETECTOR_BACKEND,



        "face_mode":

            "backend-rds-dynamic",



        "ocr_service":

            OCR_SERVICE_URL,



        "backend_authorize_url":

            BACKEND_AUTHORIZE_URL,



        "backend_face_match_url":

            BACKEND_FACE_MATCH_URL,



        "face_models_ready":

            FACE_MODELS_READY,



        "face_warmup_seconds":

            FACE_WARMUP_SECONDS

    }



@app.get("/ready")
def ready():

    if not FACE_MODELS_READY:

        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "service": "smartpark-ai",
                "version": "2.8.1",
                "face_models_ready": False,
                "warmup_error": FACE_WARMUP_ERROR
            }
        )

    return {
        "status": "ready",
        "service": "smartpark-ai",
        "version": "2.8.1",
        "face_models_ready": True,
        "face_warmup_seconds": FACE_WARMUP_SECONDS
    }



# ============================================================

# FACE ENROLL

#

# Recibe de 3 a 5 imagenes.

# Cada imagen debe tener exactamente un rostro.

#

# Genera:

# - un embedding normalizado por foto

# - promedio de embeddings

# - normalizacion L2 final

# ============================================================



@app.post("/face/enroll")

async def face_enroll(

    images: list[UploadFile] = File(...)

):



    if not (

        MIN_ENROLLMENT_IMAGES

        <=

        len(images)

        <=

        MAX_ENROLLMENT_IMAGES

    ):

        raise HTTPException(

            status_code=400,

            detail=(

                "Se requieren entre "

                f"{MIN_ENROLLMENT_IMAGES} y "

                f"{MAX_ENROLLMENT_IMAGES} "

                "imagenes para enrolamiento"

            )

        )



    embeddings = []

    sample_results = []



    for index, image in enumerate(

        images

    ):



        contents = await image.read()



        if not contents:

            raise HTTPException(

                status_code=400,

                detail=(

                    f"La imagen "

                    f"{index + 1} esta vacia"

                )

            )



        frame = decode_image(

            contents

        )



        try:

            async with FACE_INFERENCE_LOCK:

                face_data = await run_in_threadpool(

                    extract_single_face_embedding,

                    frame

                )



        except HTTPException as error:

            raise HTTPException(

                status_code=error.status_code,

                detail={

                    "image_index":

                        index,



                    "filename":

                        image.filename,



                    "error":

                        error.detail

                }

            ) from error



        embedding = face_data[

            "embedding"

        ]



        embeddings.append(

            np.asarray(

                embedding,

                dtype=np.float32

            )

        )



        sample_results.append({

            "index":

                index,



            "filename":

                image.filename,



            "quality_score":

                face_data[

                    "quality_score"

                ],



            "embedding_dimension":

                face_data[

                    "embedding_dimension"

                ],



            "facial_area":

                face_data[

                    "facial_area"

                ]

        })



    dimensions = {

        len(vector)

        for vector in embeddings

    }



    if len(dimensions) != 1:

        raise HTTPException(

            status_code=500,

            detail=(

                "Las dimensiones de los "

                "embeddings no coinciden"

            )

        )



    embedding_dimension = dimensions.pop()



    stacked = np.stack(

        embeddings,

        axis=0

    )



    mean_embedding = np.mean(

        stacked,

        axis=0

    )



    final_embedding = normalize_embedding(

        mean_embedding.tolist()

    )



    return {

        "status":

            "ok",



        "model_name":

            FACE_MODEL_NAME,



        "detector_backend":

            FACE_DETECTOR_BACKEND,



        "samples_received":

            len(images),



        "samples_used":

            len(embeddings),



        "embedding_dimension":

            embedding_dimension,



        "embedding":

            final_embedding,



        "sample_results":

            sample_results

    }





# ============================================================

# FACE

#

# Reconocimiento dinamico:

# imagen -> ArcFace -> backend /match -> RDS

# ============================================================



@app.post("/face")

async def face(

    image: UploadFile = File(...)

):



    contents = await image.read()



    frame = decode_image(

        contents

    )



    return await recognize_face_dynamic(

        frame

    )





# ============================================================

# FACE LEGACY

#

# Solo para diagnostico temporal.

# Usa el reconocimiento local anterior.

# No se utiliza para autorizacion.

# ============================================================



@app.post("/face-legacy")

async def face_legacy(

    image: UploadFile = File(...)

):



    contents = await image.read()



    frame = decode_image(

        contents

    )



    async with FACE_INFERENCE_LOCK:

        return await run_in_threadpool(

            recognize_face,

            frame

        )





# ============================================================

# VEHICLE

# YOLO11n

# ============================================================



@app.post("/vehicle")

async def vehicle(

    image: UploadFile = File(...)

):



    contents = await image.read()



    frame = decode_image(

        contents

    )



    results = model.predict(

        source=frame,



        classes=list(

            VEHICLE_CLASSES.keys()

        ),



        conf=CONFIDENCE,



        iou=IOU_THRESHOLD,



        imgsz=YOLO_IMAGE_SIZE,



        verbose=False

    )



    detections = []



    for result in results:



        if result.boxes is None:

            continue



        for box in result.boxes:



            class_id = int(

                box.cls[0]

            )



            if class_id not in VEHICLE_CLASSES:

                continue



            confidence = float(

                box.conf[0]

            )



            x1, y1, x2, y2 = map(

                int,

                box.xyxy[0]

            )



            detections.append(

                {

                    "class_id":

                        class_id,



                    "class_name":

                        VEHICLE_CLASSES[

                            class_id

                        ],



                    "confidence":

                        confidence,



                    "box": {

                        "x1":

                            x1,



                        "y1":

                            y1,



                        "x2":

                            x2,



                        "y2":

                            y2

                    }

                }

            )



    if not detections:

        return {

            "status":

                "ok",



            "vehicle_detected":

                False,



            "vehicle_type":

                None,



            "confidence":

                0.0

        }



    best_detection = max(

        detections,

        key=lambda item:

            item[

                "confidence"

            ]

    )



    return {

        "status":

            "ok",



        "vehicle_detected":

            True,



        "vehicle_type":

            best_detection[

                "class_name"

            ],



        "confidence":

            best_detection[

                "confidence"

            ]

    }





# ============================================================

# TRACKING

# YOLO11n + ByteTrack

#

# Arriba -> abajo = ENTRY

# Abajo -> arriba = EXIT

# ============================================================



def track_vehicle_video(

    video_path: str

):



    previous_centers = {}



    processed_tracks = set()



    events = []



    results = model.track(

        source=video_path,



        stream=True,



        persist=True,



        tracker=TRACKER_PATH,



        classes=list(

            VEHICLE_CLASSES.keys()

        ),



        conf=CONFIDENCE,



        iou=IOU_THRESHOLD,



        imgsz=YOLO_IMAGE_SIZE,



        verbose=False

    )



    frame_number = 0



    for result in results:



        frame_number += 1



        if result.boxes is None:

            continue



        if result.boxes.id is None:

            continue



        frame_height = (

            result.orig_shape[0]

        )



        line_y = int(

            frame_height * 0.50

        )



        boxes = (

            result.boxes.xyxy

            .cpu()

            .numpy()

        )



        track_ids = (

            result.boxes.id

            .int()

            .cpu()

            .tolist()

        )



        class_ids = (

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

            track_ids,

            class_ids,

            confidences

        ):



            _, y1, _, y2 = box



            center_y = int(

                (y1 + y2) / 2

            )



            previous_y = (

                previous_centers.get(

                    track_id

                )

            )



            if (

                previous_y is not None

                and

                track_id not in processed_tracks

            ):



                # ARRIBA -> ABAJO = ENTRY

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



                            "vehicle_type":

                                VEHICLE_CLASSES.get(

                                    class_id,

                                    "vehicle"

                                ),



                            "confidence":

                                float(

                                    confidence

                                ),



                            "frame":

                                frame_number

                        }

                    )



                    processed_tracks.add(

                        track_id

                    )



                # ABAJO -> ARRIBA = EXIT

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



                            "vehicle_type":

                                VEHICLE_CLASSES.get(

                                    class_id,

                                    "vehicle"

                                ),



                            "confidence":

                                float(

                                    confidence

                                ),



                            "frame":

                                frame_number

                        }

                    )



                    processed_tracks.add(

                        track_id

                    )



            previous_centers[

                track_id

            ] = center_y



    if not events:

        return {

            "status":

                "ok",



            "vehicle_tracked":

                True,



            "crossing_detected":

                False,



            "event_type":

                None,



            "track_id":

                None

        }



    event = events[0]



    return {

        "status":

            "ok",



        "vehicle_tracked":

            True,



        "crossing_detected":

            True,



        "event_type":

            event[

                "event_type"

            ],



        "vehicle_type":

            event[

                "vehicle_type"

            ],



        "track_id":

            event[

                "track_id"

            ],



        "confidence":

            event[

                "confidence"

            ]

    }





# ============================================================

# ENDPOINT TRACKING

# ============================================================



@app.post("/vehicle-track")

async def vehicle_track(

    video: UploadFile = File(...)

):



    suffix = ".mp4"



    if (

        video.filename

        and

        "." in video.filename

    ):



        suffix = (

            "."

            +

            video.filename

            .split(".")[-1]

        )



    contents = await video.read()



    temp_path = None



    try:



        with tempfile.NamedTemporaryFile(

            delete=False,

            suffix=suffix

        ) as temp_file:



            temp_file.write(

                contents

            )



            temp_path = (

                temp_file.name

            )



        result = track_vehicle_video(

            temp_path

        )



        return result



    finally:



        if (

            temp_path

            and

            os.path.exists(

                temp_path

            )

        ):



            os.remove(

                temp_path

            )





# ============================================================

# PROCESS

#

# ROSTRO DINAMICO

# +

# PLACA

# +

# AUTORIZACION BACKEND AWS

# ============================================================



@app.post("/process")

async def process(

    face_image: UploadFile = File(...),

    plate_image: UploadFile = File(...),

    event_type: str = Form("ENTRY")

):



    process_started_at = time.perf_counter()



    event_type = (

        event_type

        .strip()

        .upper()

    )



    if event_type not in (

        "ENTRY",

        "EXIT"

    ):



        raise HTTPException(

            status_code=400,

            detail=(

                "event_type debe ser "

                "ENTRY o EXIT"

            )

        )



    # ========================================================

    # 1. RECONOCIMIENTO FACIAL DINAMICO

    # ========================================================



    face_contents = await face_image.read()



    face_frame = decode_image(

        face_contents

    )



    face_result = await recognize_face_dynamic(

        face_frame

    )



    # ========================================================

    # 2. OCR PLACA

    # ========================================================



    plate_contents = await plate_image.read()



    ocr_started_at = time.perf_counter()



    try:



        async with httpx.AsyncClient(

            timeout=60.0

        ) as client:



            response = await client.post(

                OCR_SERVICE_URL,



                files={

                    "image": (

                        plate_image.filename

                        or

                        "plate.jpg",



                        plate_contents,



                        plate_image.content_type

                        or

                        "image/jpeg"

                    )

                }

            )



            response.raise_for_status()



            plate_result = (

                response.json()

            )



        print(
            "[OCR] Procesamiento en "
            f"{time.perf_counter() - ocr_started_at:.2f}s"
        )



    except httpx.RequestError as error:



        raise HTTPException(

            status_code=503,



            detail=(

                "No se pudo conectar "

                "con SmartPark OCR: "

                f"{error}"

            )

        ) from error



    except httpx.HTTPStatusError as error:



        raise HTTPException(

            status_code=502,



            detail=(

                "SmartPark OCR respondio "

                "con error "

                f"{error.response.status_code}"

            )

        ) from error



    # ========================================================

    # 3. DATOS ROSTRO

    # ========================================================



    face_recognized = bool(

        face_result.get(

            "recognized",

            False

        )

    )



    person_name = (

        face_result.get(

            "name"

        )

    )



    user_id = (

        face_result.get(

            "user_id"

        )

    )



    face_score = float(

        face_result.get(

            "similarity",

            0.0

        )

        or

        0.0

    )



    # ========================================================

    # 4. DATOS PLACA

    # Compatible con OCR 1.0 / OCR 1.1

    # ========================================================



    detected_plate = (

        plate_result.get(

            "detected_plate"

        )

        or

        plate_result.get(

            "plate"

        )

    )



    plate_score = float(

        plate_result.get(

            "plate_score"

        )

        or

        plate_result.get(

            "confidence"

        )

        or

        0.0

    )



    plate_detected = bool(

        plate_result.get(

            "plate_detected",

            False

        )

        or

        plate_result.get(

            "detected",

            False

        )

        or

        detected_plate

    )



    # ========================================================

    # 5. LISTO PARA AUTORIZAR

    # ========================================================



    ready_for_authorization = bool(

        face_recognized

        and

        user_id is not None

        and

        plate_detected

        and

        detected_plate

    )



    # ========================================================

    # 6. RESPUESTA

    # ========================================================



    result = {



        "status":

            "processed",



        "event_type":

            event_type,



        "ready_for_authorization":

            ready_for_authorization,



        "user_id":

            user_id,



        "person":

            person_name,



        "face_recognized":

            face_recognized,



        "face_score":

            face_score,



        "detected_plate":

            detected_plate,



        "plate_display":

            plate_result.get(

                "plate_display"

            ),



        "plate_score":

            plate_score,



        "authorization_called":

            False,



        "authorization":

            None

    }



    # ========================================================

    # 7. BACKEND AWS

    # ========================================================



    if ready_for_authorization:



        authorization_payload = {



            "user_id":

                user_id,



            "detected_plate":

                detected_plate,



            "event_type":

                event_type,



            "face_score":

                face_score,



            "plate_score":

                plate_score,



            "evidence_key":

                "ai/local-process.jpg"

        }



        print(

            "[AI] Enviando autorizacion "

            "al backend AWS..."

        )



        try:



            async with httpx.AsyncClient(

                timeout=30.0

            ) as client:



                backend_response = (

                    await client.post(

                        BACKEND_AUTHORIZE_URL,

                        json=authorization_payload

                    )

                )



                backend_response.raise_for_status()



                authorization_result = (

                    backend_response.json()

                )



            result[

                "authorization_called"

            ] = True



            result[

                "authorization"

            ] = authorization_result



            print(

                "[AI] Respuesta backend:"

            )



            print(

                authorization_result

            )



        except httpx.RequestError as error:



            result[

                "authorization_called"

            ] = True



            result[

                "authorization"

            ] = {



                "status":

                    "ERROR",



                "detail":

                    (

                        "No se pudo conectar "

                        "con backend: "

                        f"{error}"

                    )

            }



        except httpx.HTTPStatusError as error:



            result[

                "authorization_called"

            ] = True



            result[

                "authorization"

            ] = {



                "status":

                    "ERROR",



                "http_status":

                    error.response.status_code,



                "detail":

                    error.response.text

            }



    print(
        "[PROCESS] Tiempo total IA: "
        f"{time.perf_counter() - process_started_at:.2f}s"
    )

    return result
