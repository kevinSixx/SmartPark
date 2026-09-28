from pathlib import Path

import numpy as np
from deepface import DeepFace


# =========================================================
# SMARTPARK - RECONOCIMIENTO FACIAL LEGACY
# =========================================================
#
# Este modulo se conserva SOLO para el endpoint /face-legacy
# y diagnostico local.
#
# El flujo de autorizacion real NO usa este embedding fijo.
# El flujo real esta en ai/main.py:
#
#   imagen -> RetinaFace -> ArcFace -> embedding
#          -> Backend /api/v1/face-profiles/match -> RDS
#
# El warm-up de RetinaFace + ArcFace tambien se realiza en
# ai/main.py durante el startup del servicio.
# =========================================================


# =========================================================
# CONFIGURACION LEGACY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

REFERENCE_EMBEDDING = (
    BASE_DIR
    / "faces"
    / "kevin_embedding.npy"
)

MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "retinaface"

PERSON_NAME = "Kevin Rueda"

# Umbral historico usado unicamente por /face-legacy.
SIMILARITY_THRESHOLD = 0.60


# =========================================================
# FUNCIONES
# =========================================================

def normalize(vector):
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def cosine_similarity(vector_a, vector_b):
    vector_a = normalize(vector_a)
    vector_b = normalize(vector_b)

    return float(
        np.dot(
            vector_a,
            vector_b,
        )
    )


# =========================================================
# CARGAR PERFIL FACIAL LEGACY
# =========================================================

if not REFERENCE_EMBEDDING.exists():
    raise FileNotFoundError(
        f"No existe el perfil facial: "
        f"{REFERENCE_EMBEDDING}"
    )


reference_embedding = np.load(
    REFERENCE_EMBEDDING
)

reference_embedding = normalize(
    reference_embedding
)


print(
    "[FACE-LEGACY] Perfil facial local de Kevin cargado."
)


# =========================================================
# RECONOCIMIENTO LEGACY
# =========================================================

def recognize_face(frame):
    """
    Reconocimiento facial local heredado.

    IMPORTANTE:
    - No se utiliza para la autorizacion principal.
    - El flujo principal usa recognize_face_dynamic() en ai/main.py.
    - Se mantiene solo para /face-legacy y diagnostico.
    """

    try:
        representations = DeepFace.represent(
            img_path=frame,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
            align=True,
        )

        if not representations:
            return {
                "status": "no_face",
                "recognized": False,
                "name": "SIN ROSTRO",
                "similarity": 0.0,
                "facial_area": None,
            }

        # Si aparecen varias personas, utilizamos el rostro mas grande.
        def face_size(face_data):
            area = face_data.get(
                "facial_area",
                {},
            )

            width = area.get(
                "w",
                0,
            )

            height = area.get(
                "h",
                0,
            )

            return width * height

        face = max(
            representations,
            key=face_size,
        )

        current_embedding = np.array(
            face["embedding"],
            dtype=np.float32,
        )

        similarity = cosine_similarity(
            reference_embedding,
            current_embedding,
        )

        recognized = (
            similarity
            >= SIMILARITY_THRESHOLD
        )

        if recognized:
            name = PERSON_NAME
        else:
            name = "DESCONOCIDO"

        return {
            "status": "ok",
            "recognized": recognized,
            "name": name,
            "similarity": similarity,
            "facial_area": face.get(
                "facial_area"
            ),
        }

    except ValueError:
        # RetinaFace no encontro rostro.
        return {
            "status": "no_face",
            "recognized": False,
            "name": "SIN ROSTRO",
            "similarity": 0.0,
            "facial_area": None,
        }

    except Exception as error:
        print(
            f"[FACE-LEGACY] Error: "
            f"{type(error).__name__}: "
            f"{error}"
        )

        return {
            "status": "error",
            "recognized": False,
            "name": "ERROR",
            "similarity": 0.0,
            "facial_area": None,
        }
