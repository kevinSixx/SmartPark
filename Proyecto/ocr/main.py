import re
import cv2
import numpy as np

from fastapi import FastAPI, File, UploadFile, HTTPException
from paddleocr import PaddleOCR


# ============================================================
# SMARTPARK UCE
# OCR DE PLACAS
#
# Soporta:
#
# AUTO:
#   TDH-398
#   AAC-0123
#
# MOTO:
#   JG
#   505Y
#
# También mantiene un fallback alfanumérico para no limitar
# PaddleOCR únicamente a estos tres patrones.
# ============================================================


app = FastAPI(
    title="SmartPark OCR",
    version="1.1.0"
)


# ============================================================
# CONFIGURACION
# ============================================================

MIN_TEXT_CONFIDENCE = 0.25

MIN_FINAL_CONFIDENCE = 0.35


# ============================================================
# PADDLE OCR
# ============================================================

print("[OCR] Inicializando PaddleOCR...")


ocr_engine = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    show_log=False,
    use_gpu=False
)


print("[OCR] PaddleOCR listo.")


# ============================================================
# MAPAS DE CORRECCION
# ============================================================
#
# Son correcciones comunes cuando OCR confunde letras/numeros.
#
# Ejemplos:
#
# O -> 0
# I -> 1
# S -> 5
#
# o inversamente cuando esa posicion debe contener una letra.
#
# ============================================================


TO_DIGIT = {
    "O": "0",
    "Q": "0",
    "D": "0",

    "I": "1",
    "L": "1",

    "Z": "2",

    "S": "5",

    "G": "6",

    "B": "8"
}


TO_LETTER = {
    "0": "O",

    "1": "I",

    "2": "Z",

    "5": "S",

    "6": "G",

    "8": "B"
}


# ============================================================
# FORMATOS SOPORTADOS
# ============================================================
#
# L = letra
# D = digito
#
# AUTO:
#
# TDH398
# LLLDDD
#
# AAC0123
# LLLDDDD
#
# MOTO:
#
# JG505Y
# LLDDDL
#
# ============================================================


PLATE_PATTERNS = [
    {
        "name": "CAR_3L_4D",
        "vehicle_type": "CAR",
        "mask": "LLLDDDD",
        "priority": 120
    },
    {
        "name": "CAR_3L_3D",
        "vehicle_type": "CAR",
        "mask": "LLLDDD",
        "priority": 115
    },
    {
        "name": "MOTORCYCLE_2L_3D_1L",
        "vehicle_type": "MOTORCYCLE",
        "mask": "LLDDDL",
        "priority": 120
    }
]


# ============================================================
# HEALTH
# ============================================================


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "smartpark-ocr",
        "version": "1.1.0",
        "formats": [
            "LLLDDD",
            "LLLDDDD",
            "LLDDDL"
        ]
    }


# ============================================================
# NORMALIZAR TEXTO
# ============================================================


def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.upper()

    # Solamente letras y numeros.
    text = re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )

    return text


# ============================================================
# COORDENADAS DEL BOX
# ============================================================


def get_box_position(box):

    try:

        xs = [
            float(point[0])
            for point in box
        ]

        ys = [
            float(point[1])
            for point in box
        ]

        return {
            "x": min(xs),
            "y": min(ys),
            "center_x": sum(xs) / len(xs),
            "center_y": sum(ys) / len(ys)
        }

    except Exception:

        return {
            "x": 0.0,
            "y": 0.0,
            "center_x": 0.0,
            "center_y": 0.0
        }


# ============================================================
# EXTRAER TOKENS DE PADDLE OCR
# ============================================================


def extract_tokens(ocr_result):

    tokens = []

    if not ocr_result:
        return tokens


    # PaddleOCR normalmente:
    #
    # [
    #   [
    #      [box, ("ABC123", 0.99)],
    #      ...
    #   ]
    # ]
    #

    if (
        len(ocr_result) == 1
        and isinstance(
            ocr_result[0],
            list
        )
    ):

        detections = (
            ocr_result[0]
            or []
        )

    else:

        detections = (
            ocr_result
            or []
        )


    for detection in detections:

        try:

            box = detection[0]

            text_info = detection[1]

            text = str(
                text_info[0]
            )

            confidence = float(
                text_info[1]
            )


            if confidence < MIN_TEXT_CONFIDENCE:
                continue


            normalized = normalize_text(
                text
            )


            if not normalized:
                continue


            position = get_box_position(
                box
            )


            tokens.append({
                "text": text,
                "normalized": normalized,
                "confidence": confidence,
                "box": box,
                **position
            })


        except Exception:

            continue


    # Orden aproximado:
    #
    # arriba -> abajo
    # izquierda -> derecha
    #
    # Esto es importante para:
    #
    # JG
    # 505Y
    #

    tokens.sort(
        key=lambda item: (
            round(
                item["center_y"] / 20
            ),
            item["center_x"]
        )
    )


    return tokens


# ============================================================
# CORREGIR CANDIDATO SEGUN MASCARA
# ============================================================


def coerce_to_mask(
    value: str,
    mask: str
):

    if len(value) != len(mask):
        return None


    output = []

    changes = 0


    for char, expected in zip(
        value,
        mask
    ):

        # ====================================================
        # LETRA
        # ====================================================

        if expected == "L":

            if char.isalpha():

                output.append(
                    char
                )

            elif char in TO_LETTER:

                output.append(
                    TO_LETTER[char]
                )

                changes += 1

            else:

                return None


        # ====================================================
        # DIGITO
        # ====================================================

        elif expected == "D":

            if char.isdigit():

                output.append(
                    char
                )

            elif char in TO_DIGIT:

                output.append(
                    TO_DIGIT[char]
                )

                changes += 1

            else:

                return None


    return (
        "".join(output),
        changes
    )


# ============================================================
# FORMATO VISUAL
# ============================================================


def format_plate(
    plate: str,
    format_name: str
):

    if format_name == "CAR_3L_3D":

        return (
            f"{plate[:3]}-"
            f"{plate[3:]}"
        )


    if format_name == "CAR_3L_4D":

        return (
            f"{plate[:3]}-"
            f"{plate[3:]}"
        )


    if format_name == "MOTORCYCLE_2L_3D_1L":

        # Forma canónica para interfaz.
        #
        # La placa física puede estar:
        #
        # JG
        # 505Y
        #
        return (
            f"{plate[:2]}-"
            f"{plate[2:]}"
        )


    return plate


# ============================================================
# CONFIANZA COMBINADA
# ============================================================


def weighted_confidence(
    selected_tokens
):

    if not selected_tokens:
        return 0.0


    total_chars = 0

    total_score = 0.0


    for token in selected_tokens:

        length = max(
            len(
                token["normalized"]
            ),
            1
        )

        total_chars += length

        total_score += (
            token["confidence"]
            *
            length
        )


    if total_chars == 0:
        return 0.0


    return (
        total_score
        /
        total_chars
    )


# ============================================================
# GENERAR CANDIDATOS
# ============================================================


def build_candidates(
    tokens
):

    candidates = []


    if not tokens:
        return candidates


    # ========================================================
    # COMBINACIONES CONTIGUAS
    # ========================================================
    #
    # Esto permite:
    #
    # ["AAC", "0123"]
    # -> AAC0123
    #
    # ["JG", "505Y"]
    # -> JG505Y
    #
    # También prueba tokens individuales.
    # ========================================================


    max_group = min(
        4,
        len(tokens)
    )


    for start in range(
        len(tokens)
    ):

        for size in range(
            1,
            max_group + 1
        ):

            end = (
                start
                +
                size
            )


            if end > len(tokens):
                break


            selected = (
                tokens[start:end]
            )


            raw_value = "".join(
                token["normalized"]
                for token in selected
            )


            if not raw_value:
                continue


            confidence = (
                weighted_confidence(
                    selected
                )
            )


            # =================================================
            # FORMATOS CONOCIDOS
            # =================================================

            for pattern in PLATE_PATTERNS:

                coerced = (
                    coerce_to_mask(
                        raw_value,
                        pattern["mask"]
                    )
                )


                if coerced is None:
                    continue


                corrected_value, changes = (
                    coerced
                )


                score = (
                    pattern["priority"]
                    +
                    confidence * 10.0
                    -
                    changes * 0.5
                )


                candidates.append({
                    "plate": corrected_value,
                    "confidence": confidence,
                    "format": pattern["name"],
                    "vehicle_type": (
                        pattern["vehicle_type"]
                    ),
                    "score": score,
                    "changes": changes,
                    "source_tokens": [
                        token["text"]
                        for token in selected
                    ]
                })


            # =================================================
            # FALLBACK GENERICO
            # =================================================
            #
            # No queremos que OCR quede bloqueado únicamente
            # a tres patrones.
            #
            # Permitimos de 5 a 8 caracteres alfanumericos,
            # siempre que contenga letras Y números.
            # =================================================

            if (
                5
                <=
                len(raw_value)
                <=
                8
            ):

                has_letter = any(
                    char.isalpha()
                    for char in raw_value
                )

                has_digit = any(
                    char.isdigit()
                    for char in raw_value
                )


                if (
                    has_letter
                    and
                    has_digit
                ):

                    generic_score = (
                        20
                        +
                        confidence * 10.0
                    )


                    candidates.append({
                        "plate": raw_value,
                        "confidence": confidence,
                        "format": "GENERIC",
                        "vehicle_type": "UNKNOWN",
                        "score": generic_score,
                        "changes": 0,
                        "source_tokens": [
                            token["text"]
                            for token in selected
                        ]
                    })


    return candidates


# ============================================================
# ELEGIR MEJOR CANDIDATO
# ============================================================


def choose_best_candidate(
    tokens
):

    candidates = (
        build_candidates(
            tokens
        )
    )


    if not candidates:
        return None


    # Eliminar duplicados conservando
    # la mejor puntuación.

    unique = {}


    for candidate in candidates:

        key = (
            candidate["plate"],
            candidate["format"]
        )


        current = unique.get(
            key
        )


        if (
            current is None
            or
            candidate["score"]
            >
            current["score"]
        ):

            unique[key] = candidate


    candidates = list(
        unique.values()
    )


    candidates.sort(
        key=lambda item: (
            item["score"],
            item["confidence"]
        ),
        reverse=True
    )


    return candidates[0]


# ============================================================
# PREPROCESAMIENTO
# ============================================================


def build_image_variants(
    image
):

    variants = []


    # ========================================================
    # ORIGINAL
    # ========================================================

    variants.append(
        (
            "original",
            image
        )
    )


    # ========================================================
    # ESCALA DE GRISES + CLAHE
    # ========================================================

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    clahe = (
        cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )
    )


    enhanced = clahe.apply(
        gray
    )


    enhanced_bgr = cv2.cvtColor(
        enhanced,
        cv2.COLOR_GRAY2BGR
    )


    variants.append(
        (
            "enhanced",
            enhanced_bgr
        )
    )


    # ========================================================
    # SHARPEN
    # ========================================================

    blur = cv2.GaussianBlur(
        enhanced,
        (0, 0),
        1.2
    )


    sharpened = cv2.addWeighted(
        enhanced,
        1.8,
        blur,
        -0.8,
        0
    )


    sharpened_bgr = cv2.cvtColor(
        sharpened,
        cv2.COLOR_GRAY2BGR
    )


    variants.append(
        (
            "sharpened",
            sharpened_bgr
        )
    )


    return variants


# ============================================================
# OCR SOBRE UNA IMAGEN
# ============================================================


def run_ocr(
    image
):

    all_results = []


    variants = (
        build_image_variants(
            image
        )
    )


    for variant_name, variant in variants:

        try:

            result = (
                ocr_engine.ocr(
                    variant,
                    cls=True
                )
            )


            tokens = (
                extract_tokens(
                    result
                )
            )


            candidate = (
                choose_best_candidate(
                    tokens
                )
            )


            if candidate:

                candidate[
                    "image_variant"
                ] = variant_name

                candidate[
                    "tokens"
                ] = tokens

                all_results.append(
                    candidate
                )


        except Exception as error:

            print(
                f"[OCR] Error en variante "
                f"{variant_name}: {error}"
            )


    if not all_results:
        return None


    all_results.sort(
        key=lambda item: (
            item["score"],
            item["confidence"]
        ),
        reverse=True
    )


    return all_results[0]


# ============================================================
# ENDPOINT /plate
# ============================================================


@app.post("/plate")
async def detect_plate(
    image: UploadFile = File(...)
):

    try:

        image_bytes = (
            await image.read()
        )


        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail="Imagen vacía."
            )


        np_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )


        frame = cv2.imdecode(
            np_array,
            cv2.IMREAD_COLOR
        )


        if frame is None:

            raise HTTPException(
                status_code=400,
                detail="No se pudo decodificar la imagen."
            )


        print()

        print(
            "=" * 60
        )

        print(
            "[OCR] Procesando placa..."
        )


        result = (
            run_ocr(
                frame
            )
        )


        if result is None:

            print(
                "[OCR] No se encontró placa."
            )


            return {
                "status": "ok",
                "plate_detected": False,
                "detected_plate": None,
                "plate": None,
                "plate_display": None,
                "confidence": 0.0,
                "plate_score": 0.0,
                "plate_format": None,
                "vehicle_type": None,
                "ocr_lines": []
            }


        plate = result[
            "plate"
        ]


        confidence = float(
            result[
                "confidence"
            ]
        )


        plate_format = (
            result[
                "format"
            ]
        )


        vehicle_type = (
            result[
                "vehicle_type"
            ]
        )


        display = format_plate(
            plate,
            plate_format
        )


        ocr_lines = [
            {
                "text": token["text"],
                "normalized": (
                    token["normalized"]
                ),
                "confidence": float(
                    token["confidence"]
                )
            }
            for token in result[
                "tokens"
            ]
        ]


        detected = (
            confidence
            >=
            MIN_FINAL_CONFIDENCE
        )


        print(
            f"[OCR] Plate: "
            f"{plate}"
        )

        print(
            f"[OCR] Display: "
            f"{display}"
        )

        print(
            f"[OCR] Formato: "
            f"{plate_format}"
        )

        print(
            f"[OCR] Tipo: "
            f"{vehicle_type}"
        )

        print(
            f"[OCR] Confianza: "
            f"{confidence:.2%}"
        )

        print(
            f"[OCR] Variante: "
            f"{result['image_variant']}"
        )

        print(
            f"[OCR] Líneas: "
            f"{ocr_lines}"
        )


        # ====================================================
        # IMPORTANTE:
        #
        # Conservamos campos compatibles con el servicio
        # anterior para NO romper smartpark_ai.
        # ====================================================

        return {
            "status": "ok",

            "plate_detected": detected,

            # Alias compatibles
            "detected_plate": plate,
            "plate": plate,

            "plate_display": display,

            # Alias compatibles
            "confidence": confidence,
            "plate_score": confidence,

            # Nuevos datos
            "plate_format": plate_format,
            "vehicle_type": vehicle_type,

            "ocr_lines": ocr_lines,

            "image_variant": (
                result[
                    "image_variant"
                ]
            )
        }


    except HTTPException:

        raise


    except Exception as error:

        print(
            f"[OCR] ERROR: {error}"
        )


        raise HTTPException(
            status_code=500,
            detail=str(error)
        )