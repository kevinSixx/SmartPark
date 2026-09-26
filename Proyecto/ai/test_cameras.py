import cv2


for index in range(5):
    print(f"\nProbando índice {index}...")

    camera = cv2.VideoCapture(index)

    if not camera.isOpened():
        print("No disponible.")
        continue

    success, frame = camera.read()

    if not success:
        print("Abre, pero no entrega imagen.")
        camera.release()
        continue

    print(f"OK - Cámara disponible en índice {index}")

    cv2.putText(
        frame,
        f"CAMERA INDEX: {index}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        f"Camera {index}",
        frame
    )

    print("Presiona cualquier tecla para probar la siguiente.")

    cv2.waitKey(0)

    camera.release()
    cv2.destroyAllWindows()