# 13. Endpoints reales

Rutas extraídas de decoradores en el código sin importar servicios ni cargar modelos. Backend cotejado con la instantánea OpenAPI 1.7.2. La respuesta de AI/OCR/Edge se resume por inspección estática; verificación en ejecución pendiente.

| Servicio | Método | Ruta | Input | Output | Autenticación | Consumidor | Estado |
|---|---|---|---|---|---|---|---|
| BACKEND | POST | `/api/v1/access-events` | application/json: timestamp, event_type*, user_id, vehicle_id, detected_plate, face_score, plate_score, decision*, reason, evidence_key | AccessEventResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/access_events.py:80`) |
| BACKEND | GET | `/api/v1/access-events` | ninguno | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/access_events.py:99`) |
| BACKEND | GET | `/api/v1/access-events/{event_id}` | event_id (path) | AccessEventResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/access_events.py:116`) |
| BACKEND | POST | `/api/v1/access/process` | multipart/form-data: face_image*, plate_image*, event_type | JSON/estado | Sin JWT en ruta | Edge y Frontend | En código; no probado en red (`backend/app/routes/access_events.py:146`) |
| BACKEND | POST | `/api/v1/access/authorize` | application/json: user_id*, detected_plate*, event_type*, face_score, plate_score, evidence_key | AuthorizationResponse | Sin JWT en ruta | AI | En código; no probado en red (`backend/app/routes/access_events.py:344`) |
| BACKEND | POST | `/api/v1/auth/login` | application/json: username*, password* | LoginResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/auth.py:41`) |
| BACKEND | GET | `/api/v1/auth/me` | Authorization: Bearer | AuthUserResponse | Bearer | Frontend | En código; no probado en red (`backend/app/routes/auth.py:84`) |
| BACKEND | POST | `/api/v1/face-profiles/enroll` | multipart/form-data: user_id*, images* | FaceEnrollmentResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/face_profiles.py:45`) |
| BACKEND | POST | `/api/v1/face-profiles/match` | application/json: embedding*, threshold | FaceMatchResponse | Sin JWT en ruta | AI | En código; no probado en red (`backend/app/routes/face_profiles.py:66`) |
| BACKEND | GET | `/api/v1/face-profiles/{user_id}` | user_id (path) | FaceProfileResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/face_profiles.py:86`) |
| BACKEND | GET | `/api/v1/face-profiles/{user_id}/samples` | user_id (path) | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/face_profiles.py:105`) |
| BACKEND | DELETE | `/api/v1/face-profiles/{user_id}` | user_id (path) | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/face_profiles.py:123`) |
| BACKEND | POST | `/api/v1/gates/{gate_id}/open` | application/json: access_event_id, reason, observation; gate_id (path) | GateActionResponse | Bearer ADMIN/GUARD | Frontend | En código; no probado en red (`backend/app/routes/gates.py:51`) |
| BACKEND | POST | `/api/v1/gates/{gate_id}/close` | application/json: access_event_id, reason, observation; gate_id (path) | GateActionResponse | Bearer ADMIN/GUARD | Frontend | En código; no probado en red (`backend/app/routes/gates.py:210`) |
| BACKEND | GET | `/api/v1/gates/{gate_id}/actions` | gate_id (path), limit (query) | JSON/estado | Bearer ADMIN/GUARD | Frontend | En código; no probado en red (`backend/app/routes/gates.py:351`) |
| BACKEND | POST | `/api/v1/permissions` | application/json: valid_from, valid_to, user_id*, vehicle_id*, active | PermissionResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/permissions.py:22`) |
| BACKEND | GET | `/api/v1/permissions` | ninguno | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/permissions.py:29`) |
| BACKEND | GET | `/api/v1/permissions/{permission_id}` | permission_id (path) | PermissionResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/permissions.py:34`) |
| BACKEND | PATCH | `/api/v1/permissions/{permission_id}` | application/json: valid_from, valid_to, active; permission_id (path) | PermissionResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/permissions.py:39`) |
| BACKEND | GET | `/api/v1/staff` | ninguno | JSON/estado | Bearer ADMIN | Frontend | En código; no probado en red (`backend/app/routes/staff.py:48`) |
| BACKEND | GET | `/api/v1/staff/{staff_id}` | staff_id (path) | StaffAccountResponse | Bearer ADMIN | Frontend | En código; no probado en red (`backend/app/routes/staff.py:69`) |
| BACKEND | POST | `/api/v1/staff` | application/json: full_name*, username*, password*, role*, active | StaffAccountResponse | Bearer ADMIN | Frontend | En código; no probado en red (`backend/app/routes/staff.py:94`) |
| BACKEND | PATCH | `/api/v1/staff/{staff_id}` | application/json: full_name, password, role, active; staff_id (path) | StaffAccountResponse | Bearer ADMIN | Frontend | En código; no probado en red (`backend/app/routes/staff.py:118`) |
| BACKEND | POST | `/api/v1/users` | application/json: name*, institutional_id* | UserResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/users.py:20`) |
| BACKEND | GET | `/api/v1/users` | ninguno | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/users.py:28`) |
| BACKEND | GET | `/api/v1/users/{user_id}` | user_id (path) | UserResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/users.py:33`) |
| BACKEND | PATCH | `/api/v1/users/{user_id}` | application/json: name, institutional_id, status; user_id (path) | UserResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/users.py:38`) |
| BACKEND | POST | `/api/v1/vehicles` | application/json: user_id*, plate*, brand, model, color, status | VehicleResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/vehicles.py:19`) |
| BACKEND | GET | `/api/v1/vehicles` | ninguno | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/vehicles.py:26`) |
| BACKEND | GET | `/api/v1/vehicles/{vehicle_id}` | vehicle_id (path) | VehicleResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/vehicles.py:31`) |
| BACKEND | GET | `/api/v1/users/{user_id}/vehicles` | user_id (path) | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/vehicles.py:36`) |
| BACKEND | PATCH | `/api/v1/vehicles/{vehicle_id}` | application/json: user_id, plate, brand, model, color, status; vehicle_id (path) | VehicleResponse | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/routes/vehicles.py:41`) |
| BACKEND | GET | `/health` | ninguno | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/main.py:180`) |
| BACKEND | GET | `/db-check` | ninguno | JSON/estado | Sin JWT en ruta | Frontend | En código; no probado en red (`backend/app/main.py:201`) |
| AI | GET | `/health` | ninguno | JSON/estado | Sin JWT en ruta | Backend/cliente | En código; no probado en red (`ai/main.py:922`) |
| AI | GET | `/ready` | ninguno | JSON/estado | Sin JWT en ruta | Backend/cliente | En código; no probado en red (`ai/main.py:1009`) |
| AI | POST | `/face/enroll` | multipart: images (3-5) | JSON/estado | Sin JWT en ruta | Backend | En código; no probado en red (`ai/main.py:1060`) |
| AI | POST | `/face` | image | JSON/estado | Sin JWT en ruta | Backend/cliente | En código; no probado en red (`ai/main.py:1388`) |
| AI | POST | `/face-legacy` | image | JSON/estado | Sin JWT en ruta | Backend/cliente | En código; no probado en red (`ai/main.py:1436`) |
| AI | POST | `/vehicle` | image | JSON/estado | Sin JWT en ruta | Backend/cliente | En código; no probado en red (`ai/main.py:1482`) |
| AI | POST | `/vehicle-track` | video | JSON/estado | Sin JWT en ruta | Backend/cliente | En código; no probado en red (`ai/main.py:2220`) |
| AI | POST | `/process` | multipart: face_image, plate_image, event_type | JSON/estado | Sin JWT en ruta | Backend | En código; no probado en red (`ai/main.py:2360`) |
| OCR | GET | `/health` | ninguno | JSON/estado | Sin JWT en ruta | AI | En código; no probado en red (`ocr/main.py:162`) |
| OCR | POST | `/plate` | multipart: image | JSON/estado | Sin JWT en ruta | AI | En código; no probado en red (`ocr/main.py:965`) |
| EDGE | GET | `/` | ninguno | JSON/estado | Sin JWT en ruta | GuardGate local | En código; no probado en red (`edge_server_demo_gpu_model_detection_v3.py:2680`) |
| EDGE | GET | `/health` | ninguno | JSON/estado | Sin JWT en ruta | GuardGate local | En código; no probado en red (`edge_server_demo_gpu_model_detection_v3.py:2695`) |
| EDGE | GET | `/status` | ninguno | JSON/estado | Sin JWT en ruta | GuardGate local | En código; no probado en red (`edge_server_demo_gpu_model_detection_v3.py:2723`) |
| EDGE | GET | `/video` | ninguno | MJPEG | Sin JWT en ruta | GuardGate local | En código; no probado en red (`edge_server_demo_gpu_model_detection_v3.py:2728`) |
| EDGE | GET | `/demo/device` | ninguno | JSON/estado | Sin JWT en ruta | GuardGate local | En código; no probado en red (`edge_server_demo_gpu_model_detection_v3.py:2740`) |
| EDGE | POST | `/demo/trigger` | distance_cm | JSON/estado | Sin JWT en ruta | GuardGate local | DEMO; retirado por launcher (`edge_server_demo_gpu_model_detection_v3.py:2751`) |

## Hallazgos

- `/api/v1/face-profiles/{user_id}` es GET/DELETE, no POST de matrícula facial. El enrolamiento usa `POST /api/v1/face-profiles/enroll`.
- Edge de producción retira ?nicamente `/demo/trigger`; `/demo/device` permanece definido en el servidor importado.
- `/ready` solo está en AI; `/status` y `/video` pertenecen al Edge local; `/db-check` conecta a la base.
- Solo rutas de auth/me, personal y barrera contienen dependencias JWT visibles. Las demás rutas Backend requieren revisión de seguridad antes de publicación.
- Los esquemas completos Backend están en `docs/smartpark-openapi-production.json`, una instantánea no regenerada en esta auditoría.
