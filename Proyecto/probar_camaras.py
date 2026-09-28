import cv2

print("Buscando cámaras disponibles...")

for index in range(6):
    cap = cv2.VideoCapture(index)

    if cap.isOpened():
        ok, frame = cap.read()

        if ok:
            print(f"✅ Cámara encontrada en índice {index}")
        else:
            print(f"⚠ Cámara {index} abre pero no entrega imagen")

        cap.release()

    else:
        print(f"❌ Índice {index} no disponible")

print("Fin.")