# 12. CORS y red

| Servicio | CORS en código | Orígenes permitidos observados | Necesidad real |
|---|---|---|---|
| Backend | `backend/app/main.py:73-88` | `localhost` y `127.0.0.1` en 5173/5174; sitio S3 website antiguo; `https://production.d1kzks9pms1av2.amplifyapp.com` | Sí para navegador Vite/Amplify → API si distintos orígenes; API Gateway también debe responder preflight coherente |
| Edge | `edge_server_demo_gpu_model_detection_v3.py:335-347`; `edge_server.py` similar | Mismos seis orígenes | Sí para `fetch` GuardGate → `http://127.0.0.1:9000`; `<img>` MJPEG puede cargar sin CORS pero no implica acceso `fetch` |
| IA | No se halló `CORSMiddleware` en `ai/main.py` | Ninguno configurado | No para Backend → IA por HTTP servidor a servidor |
| OCR | No se halló `CORSMiddleware` en `ocr/main.py` | Ninguno configurado | No para IA → OCR por HTTP servidor a servidor |

El origen S3 website aparece como configuración anterior; verificar si aún se usa. Si Amplify despliega previews con subdominios distintos, el origen exacto de production no los permite. CORS no es autenticación: los endpoints internos Backend requieren protección propia/red. Navegador Amplify HTTPS a Edge HTTP loopback debe probarse con navegador final por políticas de contenido mixto y acceso a red local. `127.0.0.1` se refiere a **la máquina del operador**, no al servidor Amplify. `VITE_EDGE_URL` apunta a esa laptop; la cámara no se transmite desde AWS.

| Trayecto | Protocolo/destino actual | Dónde se configura | Requisito |
|---|---|---|---|
| Frontend → API Gateway/Backend | HTTPS URL de `VITE_API_URL`; vacío significa origen Frontend | `frontend/src/api/smartpark.js` | CORS y despliegue URL correctos |
| Frontend → Edge local | HTTP `127.0.0.1:9000`, `/health`, `/status`, `/video` | `frontend/src/api/edge.js` | Edge en misma PC, CORS/política navegador |
| Edge → API Gateway/Backend | HTTPS por `backend_url`; POST `/api/v1/access/process` | `smartpark_edge_config.json`, launcher | No requiere CORS; TLS y URL alcanzable |
| Backend → IA | HTTP `AI_BASE_URL/process` y `/face/enroll` | `backend/app/routes/access_events.py`, `services/face_profiles.py` | Red interna, timeout; no CORS |
| IA → OCR | HTTP `OCR_SERVICE_URL`, predeterminado `smartpark_ocr:8002/plate` | `ai/main.py` | DNS/red Docker o URL local configurada |
| IA → Backend | HTTP defaults de ALB `/face-profiles/match` y `/access/authorize` | `ai/main.py` | Red interna, proteger endpoints internos |
| Backend → RDS | PostgreSQL vía `DATABASE_URL` | `backend/app/database.py` | SG, credenciales, TLS según despliegue |
| Backend → S3 | boto3 bucket y región | `services/s3_storage.py` | IAM, bucket, política, cifrado |
| Backend → IoT | boto3 IoT Data Plane | `mqtt/client.py` | IAM, endpoint, topic de comandos |
| ESP32 → IoT → Edge | MQTT/TLS, topic detección | `entradav2 (1).ino` (no seguido por Git, compilación pendiente); `smartpark_gate_cloud.py` | `secrets.h` externo, certificados/política IoT y payload compatibles |

Ninguna llamada servidor a servidor necesita CORS; sus fallos se diagnostican por DNS, rutas, SG, IAM y TLS. No se consultaron recursos AWS en esta auditoría.
