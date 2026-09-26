from pathlib import Path

import numpy as np
from deepface import DeepFace


PERSON_DIR = Path("ai/faces/kevin")
OUTPUT_FILE = Path("ai/faces/kevin_embedding.npy")

MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "retinaface"


def main():
    images = list(PERSON_DIR.glob("*.jpg"))
    images += list(PERSON_DIR.glob("*.jpeg"))
    images += list(PERSON_DIR.glob("*.png"))

    if not images:
        print("No se encontraron imágenes.")
        return

    embeddings = []

    print(f"Procesando {len(images)} imágenes...")

    for image_path in images:
        try:
            result = DeepFace.represent(
                img_path=str(image_path),
                model_name=MODEL_NAME,
                detector_backend=DETECTOR_BACKEND,
                enforce_detection=True
            )

            vector = np.array(
                result[0]["embedding"],
                dtype=np.float32
            )

            embeddings.append(vector)

            print(
                f"[OK] {image_path.name} "
                f"→ embedding generado ({len(vector)} valores)"
            )

        except Exception as error:
            print(
                f"[ERROR] {image_path.name}: {error}"
            )

    if not embeddings:
        print("No se pudo generar ningún embedding.")
        return

    average_embedding = np.mean(
        embeddings,
        axis=0
    )

    np.save(
        OUTPUT_FILE,
        average_embedding
    )

    print()
    print(
        f"[OK] Perfil facial guardado en: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()