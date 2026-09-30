# 19. Estructura final propuesta (condicional)

Árbol objetivo de **fuente**, no árbol ya existente. Entradas «por recuperar/crear» no se han encontrado o implementado; no introducir archivos vacíos para simular completitud.

```text
SmartPark-UCE/
├── VERSION                                  (por crear tras validar release)
├── README.md                                (por redactar)
├── .gitignore
├── .dockerignore
├── docker-compose.yml                       (solo stack local)
├── firmware/
│   └── esp32/
│       ├── SmartParkUCE.ino                 (desde entradav2 (1).ino tras validar)
│       └── README.md                       (pinout/topics/payload)
├── edge/
│   ├── app/
│   │   ├── launcher.py                     (desde smartpark_edge_production.py)
│   │   ├── server.py                       (desde servidor V3, tras consolidar)
│   │   ├── gate.py                         (desde smartpark_gate_cloud.py)
│   │   └── bytetrack_smartpark.yaml        (si uso Edge se confirma)
│   ├── models/
│   │   ├── yolo11n.pt
│   │   ├── face_detection_yunet_2023mar.onnx
│   │   └── license_plate_yolov8n.pt
│   ├── installer/                           (fuente PyInstaller/Inno, solo tras diff)
│   ├── tests/                               (por crear)
│   ├── requirements.txt                    (por crear/fijar)
│   ├── .env.example                        (sin credenciales)
│   └── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/                          (8 entidades observadas)
│   │   ├── routes/                          (8 routers observados)
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── mqtt/
│   │   └── scripts/
│   ├── migrations/                         (6 revisiones Alembic)
│   ├── tests/
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example                        (por crear)
│   └── README.md
├── ai/
│   ├── app/                                (mover solo si imports se validan)
│   │   ├── main.py
│   │   ├── face_recognition.py
│   │   ├── vehicle_detection.py
│   │   └── vehicle_tracking.py
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example                        (por crear)
│   └── README.md
├── ocr/
│   ├── app/
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example                        (por crear si se parametriza)
│   └── README.md
├── frontend/
│   ├── src/                                (pages, api, components, hooks, utils)
│   ├── public/
│   ├── tests/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── package-lock.json
│   ├── .env.example                        (por crear)
│   └── README.md
├── infra/
│   ├── docker/                             (config broker/Compose auxiliar)
│   ├── aws/                                (manifiestos reales, sin secretos)
│   └── diagrams/
├── docs/
│   ├── architecture/
│   ├── evidence/
│   ├── installation/
│   ├── api/
│   ├── costs/
│   └── audit/                              (estos 20 documentos)
├── sample-data/                            (solo datos sintéticos/consentidos)
├── scripts/                                (operación/validación no secreta)
└── tests/                                  (contratos e integración global)
```

Firmware es código ejecutado por ESP32; Edge es proceso Windows que recibe MQTT y analiza cámara; Backend conserva datos/reglas y publica IoT; AI genera embeddings y orquesta reconocimiento; OCR lee matrícula; Frontend es cliente de navegador; Infra define despliegue; Docs reúne contratos/evidencias; Tests globales prueban integraciones. Esta separación evita que instalar AI arrastre cámara/Edge o que OCR dependa del Frontend. **No se justifica crear `ai/app`/`ocr/app` hasta probar imports y Docker CMD.** `secrets.h` debe permanecer fuera de Git y reemplazarse por ejemplo sin credenciales. Los pesos pueden residir en un manifiesto de descarga en vez de ZIP si licencia/tamaño lo exige. Certificados y datos biométricos reales quedan fuera del árbol entregable.
