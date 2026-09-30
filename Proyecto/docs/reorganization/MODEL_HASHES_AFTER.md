# Hashes SHA-256 después del movimiento

| Archivo en `edge/models/` | SHA-256 | Comparación |
|---|---|---|
| `yolo11n.pt` | `0EBBC80D4A7680D14987A577CD21342B65ECFD94632BD9A8DA63AE6417644EE1` | Igual al origen y a copia histórica del instalador |
| `face_detection_yunet_2023mar.onnx` | `8F2383E4DD3CFBB4553EA8718107FC0423210DC964F9F4280604804ED2552FA4` | Igual al origen y a copia histórica del instalador |
| `license_plate_yolov8n.pt` | `B7557890BF829BD0B694A6A684E30599EF0E588F305397106158C958A08DAD08` | Igual al origen y a copia histórica del instalador |

Comprobados con `Get-FileHash -Algorithm SHA256` y `python -m unittest discover -s tests -v`. La procedencia y licencia de redistribución siguen sin verificar.

