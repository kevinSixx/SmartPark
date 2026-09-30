# 17. Plan de evidencias académicas

Capturas futuras con datos de prueba y secretos/tokens/rostros de terceros ocultos. Guardar hora, versión, entorno y correlación por `event_id` cuando exista. La captura no sustituye log ni prueba repetible.

| Nº | Captura que se debe tomar | Módulo | Qué debe verse | Qué demuestra | Archivo sugerido | Pie de figura |
|---:|---|---|---|---|---|---|
| 01 | Montaje HC-SR04 | IOT | Sensor, cableado, distancia de prueba | Medición física | `01_sensor_hcsr04.png` | Sensor ultrasónico instalado en el acceso. |
| 02 | ESP32 y SG90 | IOT | Placa, servo, pines identificados | Actuación local | `02_esp32_servo.png` | Controlador y actuador de la barrera. |
| 03 | Log MQTT detección | IOT/EDGE | Topic, timestamp, payload redactado | Publicación y recepción | `03_mqtt_detection.png` | Evento del sensor recibido por Edge. |
| 04 | Consola AWS IoT Core | AWS/INFRA | Thing/política/topic sin secretos | Integración cloud | `04_iot_core.png` | Enrutamiento MQTT en AWS IoT Core. |
| 05 | DroidCam/OpenCV | EDGE | Cámara seleccionada y frame | Adquisición de vídeo | `05_droidcam.png` | Fuente de vídeo disponible para Edge. |
| 06 | YOLO11n | EDGE | Caja/confianza de vehículo | Detección | `06_yolo11n.png` | Vehículo detectado por YOLO11n. |
| 07 | ByteTrack | EDGE | Track ID persistente | Seguimiento | `07_bytetrack.png` | Identidad temporal del vehículo. |
| 08 | Cruce ENTRY/EXIT | EDGE | Línea y evento en dos direcciones | Clasificación de sentido | `08_entry_exit.png` | Cruce de línea virtual y tipo de evento. |
| 09 | YuNet | EDGE | Rostro detectado, anonimizado | Detección local de cara | `09_yunet.png` | Selección de rostro con YuNet. |
| 10 | YOLOv8n placa | EDGE | Caja de placa, datos ocultos | Detector especializado | `10_placa_yolo.png` | Localización de matrícula. |
| 11 | Envío HTTP | EDGE/BACKEND | POST multipart, status, sin imagen/token | Integración Edge–API | `11_http_post.png` | Solicitud de procesamiento de acceso. |
| 12 | API Gateway | AWS/INFRA | Stage, ruta y 2xx | Entrada pública | `12_api_gateway.png` | API Gateway encaminando al Backend. |
| 13 | Backend health/route | BACKEND | `/health`, versión 1.7.2 y request ID | Servicio activo | `13_backend.png` | Respuesta del servicio Backend. |
| 14 | RDS | BACKEND/AWS | Tabla/evento de prueba, datos ocultos | Persistencia | `14_rds.png` | Evento persistido en PostgreSQL RDS. |
| 15 | S3 | BACKEND/AWS | Objeto de prueba y metadatos sin PII | Evidencia almacenada | `15_s3.png` | Almacenamiento de muestras autorizado. |
| 16 | ALB Backend | AWS/INFRA | Target group healthy | Enrutamiento | `16_alb_backend.png` | Balanceador del Backend operativo. |
| 17 | ASG Backend | AWS/INFRA | Instancias/capacidad healthy | Escalamiento | `17_asg_backend.png` | Grupo de escalamiento del Backend. |
| 18 | ALB IA | AWS/INFRA | Target group healthy interno | Enrutamiento interno | `18_alb_ia.png` | Balanceador interno de IA. |
| 19 | ASG IA | AWS/INFRA | Instancias y health | Escalamiento IA | `19_asg_ia.png` | Grupo de escalamiento de IA. |
| 20 | RetinaFace | AI | Área facial y confidence de prueba | Detección facial cloud | `20_retinaface.png` | Detección facial mediante RetinaFace. |
| 21 | ArcFace | AI | Dimensión embedding y similitud, sin vector | Comparación facial | `21_arcface.png` | Embedding y comparación de identidad. |
| 22 | PaddleOCR | OCR | Imagen anonimizada, placa inferida/confianza | Lectura de caracteres | `22_paddleocr.png` | Reconocimiento OCR de matrícula. |
| 23 | AUTHORIZED | BACKEND | Decisión, evento, permiso coincidente | Acceso permitido | `23_authorized.png` | Decisión autorizada con criterios cumplidos. |
| 24 | REJECTED | BACKEND | Motivo y evento de prueba | Acceso denegado | `24_rejected.png` | Rechazo ante criterios incumplidos. |
| 25 | OPEN/CLOSE | IOT/BACKEND | Comando IoT y barrera física | Actuación completa | `25_barrera.png` | Apertura y cierre de la barrera. |
| 26 | Frontend ADMIN/GUARD | FRONTEND | Dos vistas por rol | Experiencia y roles | `26_frontend_roles.png` | Interfaces administrativas y de guardia. |
| 27 | Historial/auditoría | FRONTEND | Tabla con IDs/fechas de prueba | Trazabilidad | `27_historial.png` | Historial de accesos y acciones. |
| 28 | Error/desconexión | EDGE/FRONTEND | Estado offline y recuperación | Resiliencia | `28_desconexion.png` | Comportamiento ante pérdida de conexión. |

Relacionar cada imagen con pasos del [plan de pruebas](14_PLAN_PRUEBAS_LOCAL.md), commit/tag y entorno. Confirmar que capturas AWS representan la arquitectura realmente desplegada; no inventar ALB/ASG por el contexto funcional.
