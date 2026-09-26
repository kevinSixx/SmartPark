# ============================================================
# SMARTPARK UCE
# PRUEBA DE OCR PARA MATRÍCULAS
# DroidCam + PaddleOCR
# ============================================================

import os

# IMPORTANTE:
# Desactivamos oneDNN / MKLDNN porque en tu instalación
# está provocando el error:
# ConvertPirAttribute2RuntimeAttribute...
os.environ["FLAGS_use_mkldnn"] = "0"

# Evita una comprobación innecesaria de servidores de modelos
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"


import cv2
from paddleocr import PaddleOCR


# ============================================================
# CONFIGURACIÓN
# ============================================================

# DroidCam virtual en Windows
CAMERA_INDEX = 0

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720


# ============================================================
# CARGAR PADDLE OCR
# ============================================================

print()
print("========================================")
print(" SMARTPARK UCE - OCR DE MATRICULAS")
print("========================================")
print()

print("[OCR] Cargando PaddleOCR...")


try:

    ocr = PaddleOCR(

        # Solo queremos OCR normal
        use_doc_orientation_classify=False,

        use_doc_unwarping=False,

        use_textline_orientation=False,

        # IMPORTANTE PARA TU ERROR
        enable_mkldnn=False,

        # Forzamos CPU
        device="cpu"
    )


    print("[OCR] PaddleOCR listo. ✅")


except Exception as error:

    print()
    print("[ERROR] No se pudo cargar PaddleOCR")
    print(type(error).__name__)
    print(str(error))

    raise SystemExit


# ============================================================
# ABRIR CÁMARA
# ============================================================

print()
print("[CAMERA] Abriendo DroidCam...")


camera = cv2.VideoCapture(
    CAMERA_INDEX
)


if not camera.isOpened():

    print()
    print(
        "[CAMERA] ERROR: "
        "No se pudo abrir DroidCam."
    )

    raise SystemExit


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


print()
print("========================================")
print(" INSTRUCCIONES")
print("========================================")
print()
print("Coloca una placa frente a la cámara.")
print()
print("C = capturar y analizar matrícula")
print("Q = salir")
print()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    success, frame = camera.read()


    if not success:

        print(
            "[CAMERA] No se pudo leer el frame."
        )

        break


    # Creamos copia para dibujar texto
    preview = frame.copy()


    # ========================================================
    # TEXTO EN PANTALLA
    # ========================================================

    cv2.putText(
        preview,
        "SMARTPARK UCE - OCR MATRICULA",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    cv2.putText(
        preview,
        "Coloca la placa frente a la camara",
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )


    cv2.putText(
        preview,
        "C = ANALIZAR    Q = SALIR",
        (30, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


    # ========================================================
    # MOSTRAR CÁMARA
    # ========================================================

    cv2.imshow(
        "SmartPark - OCR de Matricula",
        preview
    )


    key = cv2.waitKey(1) & 0xFF


    # ========================================================
    # PRESIONAR C
    # ========================================================

    if key == ord("c"):

        print()
        print(
            "----------------------------------------"
        )

        print(
            "[PLATE] Capturando imagen..."
        )


        # Guardamos el frame para poder revisarlo
        debug_path = (
            "ai/debug_plate_frame.jpg"
        )


        cv2.imwrite(
            debug_path,
            frame
        )


        print(
            f"[PLATE] Imagen guardada en: "
            f"{debug_path}"
        )


        print(
            "[OCR] Analizando texto..."
        )


        try:

            # ================================================
            # PADDLE OCR
            # ================================================

            results = ocr.predict(
                frame
            )


            print()
            print(
                "========== RESULTADO OCR =========="
            )


            if not results:

                print(
                    "[OCR] No se encontró texto."
                )


            else:

                for index, result in enumerate(
                    results,
                    start=1
                ):

                    print()
                    print(
                        f"[OCR] Resultado #{index}"
                    )

                    print(
                        "--------------------------------"
                    )

                    # PaddleOCR imprime:
                    # rec_texts
                    # rec_scores
                    # cajas
                    # etc.
                    result.print()


            print()
            print(
                "==================================="
            )


        except Exception as error:

            print()
            print(
                "========== ERROR OCR =============="
            )

            print(
                f"Tipo: "
                f"{type(error).__name__}"
            )

            print(
                f"Detalle: "
                f"{error}"
            )

            print(
                "==================================="
            )


    # ========================================================
    # PRESIONAR Q
    # ========================================================

    elif key == ord("q"):

        print()
        print(
            "[SMARTPARK] Cerrando..."
        )

        break


# ============================================================
# CERRAR
# ============================================================

camera.release()

cv2.destroyAllWindows()


print()
print(
    "[SMARTPARK] Test de matrícula finalizado."
)