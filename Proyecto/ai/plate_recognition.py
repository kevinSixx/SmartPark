# ============================================================
# SMARTPARK UCE
# MODULO DE RECONOCIMIENTO DE MATRICULAS
# PaddleOCR
# ============================================================

import os

# Evitar problema oneDNN que ya encontramos en tu equipo
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import re
import cv2
from paddleocr import PaddleOCR


# ============================================================
# CONFIGURACION
# ============================================================

MIN_OCR_CONFIDENCE = 0.55

cv2.setNumThreads(1)


# ============================================================
# CARGAR OCR
# ============================================================

print("[PLATE] Cargando PaddleOCR...")


ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False,
    device="cpu",
    cpu_threads=2,
)


print("[PLATE] PaddleOCR listo.")


# ============================================================
# LIMPIAR TEXTO
# ============================================================

def clean_text(text):

    text = str(text).upper().strip()

    text = re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )

    return text


# ============================================================
# CORREGIR ERRORES TIPICOS OCR
# ============================================================

def correct_plate_text(text):

    if len(text) not in (6, 7):
        return text


    letters = text[:3]
    numbers = text[3:]


    letter_fix = {
        "0": "O",
        "1": "I",
        "2": "Z",
        "5": "S",
        "8": "B",
    }


    number_fix = {
        "O": "0",
        "Q": "0",
        "D": "0",
        "I": "1",
        "L": "1",
        "Z": "2",
        "S": "5",
        "B": "8",
    }


    corrected_letters = "".join(
        letter_fix.get(character, character)
        for character in letters
    )


    corrected_numbers = "".join(
        number_fix.get(character, character)
        for character in numbers
    )


    return (
        corrected_letters
        +
        corrected_numbers
    )


# ============================================================
# VALIDAR FORMATO
# ============================================================

def is_valid_plate(text):

    return bool(
        re.fullmatch(
            r"[A-Z]{3}[0-9]{3,4}",
            text
        )
    )


# ============================================================
# FORMATO VISUAL
# ============================================================

def display_plate(text):

    if not text:
        return ""

    return (
        text[:3]
        +
        "-"
        +
        text[3:]
    )


# ============================================================
# EXTRAER RESULTADO DE PADDLE
# ============================================================

def get_result_data(result):

    try:

        data = result.json

        if callable(data):
            data = data()


        if (
            isinstance(data, dict)
            and
            "res" in data
        ):

            data = data["res"]


        return data


    except Exception as error:

        print(
            f"[PLATE] Error leyendo OCR: {error}"
        )

        return {}


# ============================================================
# RECONOCER MATRICULA
# ============================================================

def recognize_plate(frame):
    """
    Recibe un frame completo de OpenCV.

    PaddleOCR busca texto en toda la escena y
    nosotros filtramos solamente textos que
    tengan formato de matricula.

    Retorna por ejemplo:

    {
        "detected": True,
        "plate": "IDH398",
        "plate_display": "IDH-398",
        "confidence": 0.99
    }
    """

    try:

        # ----------------------------------------------------
        # REDUCIR SOLO SI LA IMAGEN ES DEMASIADO GRANDE
        # ----------------------------------------------------

        height, width = frame.shape[:2]


        if width > 960:

            scale = 960 / width

            new_height = int(
                height * scale
            )


            frame_ocr = cv2.resize(
                frame,
                (
                    960,
                    new_height
                )
            )

        else:

            frame_ocr = frame


        # ----------------------------------------------------
        # OCR UNA SOLA VEZ
        # ----------------------------------------------------

        results = ocr.predict(
            frame_ocr
        )


        candidates = []


        # ----------------------------------------------------
        # REVISAR TEXTOS
        # ----------------------------------------------------

        for result in results:

            data = get_result_data(
                result
            )


            texts = data.get(
                "rec_texts",
                []
            )


            scores = data.get(
                "rec_scores",
                []
            )


            for index, raw_text in enumerate(
                texts
            ):

                try:

                    confidence = float(
                        scores[index]
                    )

                except Exception:

                    confidence = 0.0


                if (
                    confidence
                    < MIN_OCR_CONFIDENCE
                ):

                    continue


                normalized = clean_text(
                    raw_text
                )


                normalized = correct_plate_text(
                    normalized
                )


                if not is_valid_plate(
                    normalized
                ):

                    continue


                candidates.append(
                    {
                        "detected": True,

                        "plate": normalized,

                        "plate_display":
                            display_plate(
                                normalized
                            ),

                        "confidence":
                            confidence,

                        "raw_text":
                            str(raw_text),
                    }
                )


        # ----------------------------------------------------
        # NO ENCONTRO MATRICULA
        # ----------------------------------------------------

        if not candidates:

            return {
                "detected": False,
                "plate": None,
                "plate_display": None,
                "confidence": 0.0,
                "raw_text": None,
            }


        # ----------------------------------------------------
        # MEJOR CANDIDATO
        # ----------------------------------------------------

        best = max(
            candidates,
            key=lambda item:
                item["confidence"]
        )


        return best


    except Exception as error:

        print(
            f"[PLATE] Error: "
            f"{type(error).__name__}: "
            f"{error}"
        )


        return {
            "detected": False,
            "plate": None,
            "plate_display": None,
            "confidence": 0.0,
            "raw_text": None,
        }