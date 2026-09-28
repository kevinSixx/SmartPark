import os
import re

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

import cv2
from paddleocr import PaddleOCR


MIN_OCR_CONFIDENCE = 0.55

cv2.setNumThreads(1)


print("[OCR] Cargando PaddleOCR...")


ocr = PaddleOCR(
    use_angle_cls=False,
    lang="en",
    use_gpu=False,
    show_log=False,
    enable_mkldnn=False,
    cpu_threads=2,
)


print("[OCR] PaddleOCR listo.")


def clean_text(text: str) -> str:

    text = str(text).upper().strip()

    return re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )


def correct_plate_text(text: str) -> str:

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

    letters = "".join(
        letter_fix.get(c, c)
        for c in letters
    )

    numbers = "".join(
        number_fix.get(c, c)
        for c in numbers
    )

    return letters + numbers


def is_valid_plate(text: str) -> bool:

    return bool(
        re.fullmatch(
            r"[A-Z]{3}[0-9]{3,4}",
            text
        )
    )


def display_plate(text: str) -> str:

    if not text:
        return ""

    return text[:3] + "-" + text[3:]


def recognize_plate(frame):

    if frame is None:

        return {
            "detected": False,
            "plate": None,
            "plate_display": None,
            "confidence": 0.0,
        }


    height, width = frame.shape[:2]


    if width > 960:

        scale = 960 / width

        frame = cv2.resize(
            frame,
            (
                960,
                int(height * scale)
            )
        )


    results = ocr.ocr(
        frame,
        cls=False
    )


    candidates = []


    if not results:

        return {
            "detected": False,
            "plate": None,
            "plate_display": None,
            "confidence": 0.0,
        }


    for page in results:

        if page is None:
            continue

        for line in page:

            if (
                line is None
                or len(line) < 2
            ):
                continue


            raw_text = line[1][0]

            confidence = float(
                line[1][1]
            )


            if confidence < MIN_OCR_CONFIDENCE:
                continue


            text = clean_text(
                raw_text
            )

            text = correct_plate_text(
                text
            )


            if is_valid_plate(text):

                candidates.append(
                    {
                        "plate": text,
                        "confidence": confidence,
                    }
                )


    if not candidates:

        return {
            "detected": False,
            "plate": None,
            "plate_display": None,
            "confidence": 0.0,
        }


    best = max(
        candidates,
        key=lambda item: item["confidence"]
    )


    return {
        "detected": True,
        "plate": best["plate"],
        "plate_display": display_plate(
            best["plate"]
        ),
        "confidence": float(
            best["confidence"]
        ),
    }