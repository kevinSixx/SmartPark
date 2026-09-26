import cv2
import numpy as np
from deepface import DeepFace


# =========================================================
# CONFIGURACIÓN
# =========================================================

CAMERA_INDEX = 0

REFERENCE_EMBEDDING = "ai/faces/kevin_embedding.npy"

MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "retinaface"

PERSON_NAME = "Kevin Rueda"


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
        np.dot(vector_a, vector_b)
    )


# =========================================================
# CARGAR PERFIL DE KEVIN
# =========================================================

reference_embedding = np.load(
    REFERENCE_EMBEDDING
)

reference_embedding = normalize(
    reference_embedding
)

print("[FACE] Perfil de Kevin cargado.")


# =========================================================
# CÁMARA
# =========================================================

camera = cv2.VideoCapture(
    CAMERA_INDEX
)

if not camera.isOpened():
    print("[CAMERA] No se pudo abrir la cámara.")
    raise SystemExit


camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)


print()
print("========================================")
print(" SMARTPARK - PRUEBA DE RECONOCIMIENTO")
print("========================================")
print()
print("C = capturar y reconocer")
print("Q = salir")
print()


while True:

    success, frame = camera.read()

    if not success:
        print("[CAMERA] No se pudo leer frame.")
        break


    preview = frame.copy()


    cv2.putText(
        preview,
        "Mira de frente a la camara",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    cv2.putText(
        preview,
        "C = RECONOCER   Q = SALIR",
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )


    cv2.imshow(
        "SmartPark - Reconocimiento",
        preview
    )


    key = cv2.waitKey(1) & 0xFF


    # =====================================================
    # CAPTURAR Y RECONOCER
    # =====================================================

    if key == ord("c"):

        print()
        print("----------------------------------------")
        print("[FACE] Analizando rostro...")
        print("----------------------------------------")


        try:

            result = DeepFace.represent(
                img_path=frame,
                model_name=MODEL_NAME,
                detector_backend=DETECTOR_BACKEND,
                enforce_detection=True,
                align=True
            )


            if not result:
                print("[FACE] No se encontró rostro.")
                continue


            face = result[0]


            current_embedding = np.array(
                face["embedding"],
                dtype=np.float32
            )


            similarity = cosine_similarity(
                reference_embedding,
                current_embedding
            )


            percentage = similarity * 100


            print(
                f"[FACE] Similitud con Kevin: "
                f"{percentage:.2f}%"
            )


            area = face.get(
                "facial_area",
                {}
            )


            x = int(area.get("x", 0))
            y = int(area.get("y", 0))
            w = int(area.get("w", 0))
            h = int(area.get("h", 0))


            # Por ahora usamos 60 % como referencia.
            if similarity >= 0.60:

                name = PERSON_NAME
                color = (0, 255, 0)

                print(
                    f"[RESULTADO] IDENTIFICADO: "
                    f"{PERSON_NAME}"
                )

            else:

                name = "DESCONOCIDO"
                color = (0, 0, 255)

                print(
                    "[RESULTADO] DESCONOCIDO"
                )


            result_frame = frame.copy()


            cv2.rectangle(
                result_frame,
                (x, y),
                (x + w, y + h),
                color,
                3
            )


            cv2.putText(
                result_frame,
                f"{name} {percentage:.1f}%",
                (
                    x,
                    max(y - 15, 30)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )


            cv2.imshow(
                "Resultado SmartPark",
                result_frame
            )


        except Exception as error:

            print()
            print("[ERROR REAL]")

            print(
                type(error).__name__
            )

            print(
                str(error)
            )


    elif key == ord("q"):
        break


camera.release()

cv2.destroyAllWindows()

print("[SMARTPARK] Prueba finalizada.")