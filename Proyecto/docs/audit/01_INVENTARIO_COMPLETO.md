# 01. Inventario completo

Fecha: 2026-09-29. Rutas relativas a `Proyecto/`. Clasificación estática: una ausencia de referencia textual no demuestra falta de uso; se revisaron además imports, Docker, scripts y referencias de rutas. No se enumeran dependencias, cachés ni builds internos. Los archivos del instalador están ignorados por Git.

| Ruta | Tipo | Módulo | Función | Estado | Referenciado por | Riesgo |
|---|---|---|---|---|---|---|---|
| `.pytest_cache/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `.venv/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `ai/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/app/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/app/models/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/app/mqtt/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/app/routes/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/app/schemas/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/app/scripts/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/app/services/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/migrations/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/migrations/versions/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `backend/tests/__pycache__/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `frontend/dist/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `frontend/node_modules/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `frontend/smartpark-amplify/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `node_modules/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `smartpark_edge_installer/build/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `smartpark_edge_installer/dist/` | directorio | GENERADO | Dependencias, caché o build local | GENERADO | instalación/compilación | MEDIO |
| `.dockerignore` | sin extensión | AWS/INFRA | recurso aws/infra | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `.env` | sin extensión | CONFIGURACIÓN | Configuración local; valores omitidos | REQUIERE VERIFICACIÓN MANUAL | ai/plate_recognition.py, ai/test_plate_ocr.py (+más) | ALTO |
| `.env.example` | example | CONFIGURACIÓN | recurso configuración | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `.gitignore` | sin extensión | CONFIGURACIÓN | recurso configuración | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `ai.zip` | zip | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `ai/.dockerignore` | sin extensión | AWS/INFRA | recurso aws/infra | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `ai/__init__.py` | py | AI | código ai | PROBABLEMENTE ACTUAL | smartpark_edge_installer/smartpark_launcher_release_v2.py | BAJO |
| `ai/bytetrack_smartpark.yaml` | yaml | AI | recurso ai | PROBABLEMENTE ACTUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `ai/debug_face_frame.jpg` | jpg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `ai/debug_plate_frame.jpg` | jpg | AI | recurso ai | PROBABLEMENTE ACTUAL | ai/test_plate_ocr.py | BAJO |
| `ai/Dockerfile` | sin extensión | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `ai/enroll_face.py` | py | AI | código ai | PROBABLEMENTE ACTUAL | backend/app/routes/face_profiles.py, backend/app/services/face_profiles.py | BAJO |
| `ai/face_recognition.py` | py | AI | código ai | PROBABLEMENTE ACTUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `ai/faces/Damian/damia2.jpeg` | jpeg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | ALTO |
| `ai/faces/Damian/damian1.jpeg` | jpeg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | ALTO |
| `ai/faces/Damian/damian3.jpeg` | jpeg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | ALTO |
| `ai/faces/Damian/damian4.jpeg` | jpeg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | ALTO |
| `ai/faces/Damian/damianfotonueva2.jpeg` | jpeg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | ALTO |
| `ai/faces/kevin/foto1.jpeg` | jpeg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | ALTO |
| `ai/faces/kevin/foto2.jpeg` | jpeg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | ALTO |
| `ai/faces/kevin/foto3.jpeg` | jpeg | AI | recurso ai | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | ALTO |
| `ai/faces/kevin_embedding.npy` | npy | AI | recurso ai | PROBABLEMENTE ACTUAL | ai/enroll_face.py, ai/face_recognition.py (+más) | ALTO |
| `ai/main.py` | py | AI | código ai | ACTUAL | ai/enroll_face.py, ai/face_recognition.py (+más) | BAJO |
| `ai/mock_esp32.py` | py | AI | código ai | DEMO | Sin mención estática; verificar | BAJO |
| `ai/plate_recognition.py` | py | AI | código ai | LEGACY | ai/smartpark_demo_local.py | MEDIO |
| `ai/requirements.txt` | txt | AI | recurso ai | ACTUAL | Sin mención estática; verificar | BAJO |
| `ai/smartpark_demo_local.py` | py | AI | código ai | DEMO | Sin mención estática; verificar | BAJO |
| `ai/test_cameras.py` | py | TEST | código test | TEST | Sin mención estática; verificar | BAJO |
| `ai/test_face_recognition_once.py` | py | TEST | código test | TEST | Sin mención estática; verificar | BAJO |
| `ai/test_plate_ocr.py` | py | TEST | código test | TEST | Sin mención estática; verificar | BAJO |
| `ai/vehicle_detection.py` | py | AI | código ai | PROBABLEMENTE ACTUAL | ai/main.py | BAJO |
| `ai/vehicle_tracking.py` | py | AI | código ai | PROBABLEMENTE ACTUAL | edge_server.py, edge_server_demo_gpu_model_detection_v3.py (+más) | BAJO |
| `backend/.dockerignore` | sin extensión | AWS/INFRA | recurso aws/infra | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `backend/alembic.ini` | ini | BACKEND | recurso backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/app/__init__.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | smartpark_edge_installer/smartpark_launcher_release_v2.py | BAJO |
| `backend/app/database.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/access_event.py (+más) | BAJO |
| `backend/app/main.py` | py | BACKEND | código backend | ACTUAL | ai/enroll_face.py, ai/face_recognition.py (+más) | BAJO |
| `backend/app/models/__init__.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | smartpark_edge_installer/smartpark_launcher_release_v2.py | BAJO |
| `backend/app/models/access_event.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/__init__.py (+más) | BAJO |
| `backend/app/models/face_profile.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/__init__.py (+más) | BAJO |
| `backend/app/models/face_sample.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/models/__init__.py, backend/app/models/user.py (+más) | BAJO |
| `backend/app/models/gate_action.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/routes/gates.py, backend/app/scripts/create_guard_tables.py (+más) | BAJO |
| `backend/app/models/permission.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/__init__.py (+más) | BAJO |
| `backend/app/models/staff_account.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/models/gate_action.py, backend/app/routes/auth.py (+más) | BAJO |
| `backend/app/models/user.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/mock_esp32.py (+más) | BAJO |
| `backend/app/models/vehicle.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `backend/app/mqtt/__init__.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | smartpark_edge_installer/smartpark_launcher_release_v2.py | BAJO |
| `backend/app/mqtt/client.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/mock_esp32.py (+más) | BAJO |
| `backend/app/routes/__init__.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | smartpark_edge_installer/smartpark_launcher_release_v2.py | BAJO |
| `backend/app/routes/access_events.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/access_event.py (+más) | BAJO |
| `backend/app/routes/auth.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `backend/app/routes/face_profiles.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/face_profile.py (+más) | BAJO |
| `backend/app/routes/gates.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/mock_esp32.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `backend/app/routes/permissions.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/permission.py (+más) | BAJO |
| `backend/app/routes/staff.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/gate_action.py (+más) | BAJO |
| `backend/app/routes/users.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/access_event.py (+más) | BAJO |
| `backend/app/routes/vehicles.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/smartpark_demo_local.py, backend/app/main.py (+más) | BAJO |
| `backend/app/schemas/__init__.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | smartpark_edge_installer/smartpark_launcher_release_v2.py | BAJO |
| `backend/app/schemas/access_event.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/__init__.py (+más) | BAJO |
| `backend/app/schemas/auth.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `backend/app/schemas/face_profile.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/__init__.py (+más) | BAJO |
| `backend/app/schemas/gate_action.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/models/gate_action.py, backend/app/routes/gates.py (+más) | BAJO |
| `backend/app/schemas/permission.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/__init__.py (+más) | BAJO |
| `backend/app/schemas/staff_account.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/models/gate_action.py, backend/app/models/staff_account.py (+más) | BAJO |
| `backend/app/schemas/user.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/mock_esp32.py (+más) | BAJO |
| `backend/app/schemas/vehicle.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `backend/app/scripts/create_admin.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/app/scripts/create_guard_tables.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/app/services/__init__.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | smartpark_edge_installer/smartpark_launcher_release_v2.py | BAJO |
| `backend/app/services/access_events.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/access_event.py (+más) | BAJO |
| `backend/app/services/auth.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `backend/app/services/authorization.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | BAJO |
| `backend/app/services/face_profiles.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/face_profile.py (+más) | BAJO |
| `backend/app/services/gate_actions.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/models/gate_action.py, backend/app/routes/gates.py (+más) | BAJO |
| `backend/app/services/permissions.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/permission.py (+más) | BAJO |
| `backend/app/services/s3_storage.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/services/face_profiles.py | BAJO |
| `backend/app/services/staff_accounts.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/models/gate_action.py, backend/app/models/staff_account.py (+más) | BAJO |
| `backend/app/services/users.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | backend/app/main.py, backend/app/models/access_event.py (+más) | BAJO |
| `backend/app/services/vehicles.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/smartpark_demo_local.py, backend/app/main.py (+más) | BAJO |
| `backend/Dockerfile` | sin extensión | BACKEND | recurso backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/migrations/env.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | ai/main.py, ai/plate_recognition.py (+más) | BAJO |
| `backend/migrations/README` | sin extensión | BACKEND | recurso backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/migrations/script.py.mako` | mako | BACKEND | recurso backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/migrations/versions/0945aa4d18a8_add_face_profiles_and_samples.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/migrations/versions/285c86e13beb_create_vehicles_permissions_and_access_.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/migrations/versions/7f2c9d1a4b6e_add_staff_accounts_and_gate_actions.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/migrations/versions/8e1b0efdf278_add_face_profiles_and_samples.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/migrations/versions/967b3f6f02f3_add_audit_timestamps.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/migrations/versions/dda2992a9d8b_create_users_table.py` | py | BACKEND | código backend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/requirements.txt` | txt | BACKEND | recurso backend | ACTUAL | Sin mención estática; verificar | BAJO |
| `backend/tests/__init__.py` | py | TEST | código test | TEST | smartpark_edge_installer/smartpark_launcher_release_v2.py | BAJO |
| `backend/tests/conftest.py` | py | TEST | código test | TEST | Sin mención estática; verificar | BAJO |
| `backend/tests/test_api.py` | py | TEST | código test | TEST | Sin mención estática; verificar | BAJO |
| `certs/camera/AmazonRootCA1.pem` | pem | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | mqtt_camera_test.py, smartpark_edge_config.json (+más) | MEDIO |
| `certs/camera/camera-certificate.pem.crt` | crt | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | mqtt_camera_test.py, smartpark_edge_config.json (+más) | MEDIO |
| `certs/camera/camera-private.pem.key` | key | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | mqtt_camera_test.py, smartpark_edge_config.json (+más) | ALTO |
| `docker-compose.yml` | yml | AWS/INFRA | recurso aws/infra | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `docs/smartpark-openapi-production.json` | json | DOCUMENTACIÓN | recurso documentación | REQUIERE VERIFICACIÓN MANUAL | frontend/tests/openapi-contract.test.js | MEDIO |
| `entradav2 (1).ino` | ino | IOT | Firmware ESP32: HC-SR04, SG90, Wi-Fi, MQTT/TLS | REQUIERE VERIFICACIÓN MANUAL | `secrets.h` ausente; AWS IoT Core y Edge | ALTO |
| `edge_server.py` | py | EDGE | código edge | REQUIERE VERIFICACIÓN MANUAL | edge_server_demo_gpu_model_detection_v3.py, smartpark_edge_installer/smartpark_edge.py (+más) | MEDIO |
| `edge_server_demo_gpu_model_detection_v3.py` | py | EDGE | código edge | PROBABLEMENTE ACTUAL | smartpark_edge_production.py | BAJO |
| `frontend.rar` | rar | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `frontend.zip` | zip | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `frontend/.env` | sin extensión | CONFIGURACIÓN | Configuración local; valores omitidos | REQUIERE VERIFICACIÓN MANUAL | ai/plate_recognition.py, ai/test_plate_ocr.py (+más) | ALTO |
| `frontend/.gitignore` | sin extensión | CONFIGURACIÓN | recurso configuración | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `frontend/eslint.config.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/index.html` | html | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/package-lock.json` | json | CONFIGURACIÓN | recurso configuración | ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/package.json` | json | CONFIGURACIÓN | recurso configuración | ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/public/favicon.svg` | svg | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/public/icons.svg` | svg | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/README.md` | md | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/README_SMARTPARK_FRONTEND.md` | md | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/smartpark-amplify-v2.zip` | zip | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `frontend/smartpark-amplify-v3.zip` | zip | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `frontend/smartpark-amplify-v4.zip` | zip | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `frontend/smartpark-amplify.zip` | zip | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `frontend/src/api/edge.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | frontend/tests/openapi-contract.test.js | BAJO |
| `frontend/src/api/smartpark.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | frontend/tests/frontend-flows.test.js, frontend/tests/openapi-contract.test.js | BAJO |
| `frontend/src/App.css` | css | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/App.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/assets/hero.png` | png | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/assets/react.svg` | svg | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/assets/vite.svg` | svg | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/components/Header.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/components/Layout.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/components/RequireRole.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/components/Sidebar.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/components/TableFilters.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/hooks/useApi.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/index.css` | css | FRONTEND | recurso frontend | PROBABLEMENTE ACTUAL | frontend/src/main.jsx | BAJO |
| `frontend/src/index.css.backup` | backup | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `frontend/src/main.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/AccessControl.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/AccessHistory.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/Dashboard.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/FaceEnrollment.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/GateAudit.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/GuardGate.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | edge_server.py | BAJO |
| `frontend/src/pages/Login.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/Permissions.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/Staff.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/Users.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/pages/Vehicles.jsx` | jsx | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/utils/faceEnrollment.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | frontend/tests/frontend-flows.test.js | BAJO |
| `frontend/src/utils/formatters.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/src/utils/loginValidation.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | frontend/tests/frontend-flows.test.js | BAJO |
| `frontend/src/utils/session.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | frontend/src/api/smartpark.js | BAJO |
| `frontend/tests/frontend-flows.test.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/tests/openapi-contract.test.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `frontend/vite.config.js` | js | FRONTEND | código frontend | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `models/smartpark/face_detection_yunet_2023mar.onnx` | onnx | MODELO | modelo inferencia | PROBABLEMENTE ACTUAL | edge_server_demo_gpu_model_detection_v3.py, smartpark_edge_installer/build_smartpark_exe_v2.ps1 (+más) | BAJO |
| `models/smartpark/license_plate_yolov8n.pt` | pt | MODELO | modelo inferencia | PROBABLEMENTE ACTUAL | edge_server_demo_gpu_model_detection_v3.py, smartpark_edge_installer/build_smartpark_exe_v2.ps1 (+más) | BAJO |
| `mosquitto/mosquitto.conf` | conf | AWS/INFRA | recurso aws/infra | REQUIERE VERIFICACIÓN MANUAL | docker-compose.yml | MEDIO |
| `mqtt_camera_test.py` | py | TEST | código test | TEST | Sin mención estática; verificar | BAJO |
| `ocr/Dockerfile` | sin extensión | OCR | recurso ocr | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `ocr/main.py` | py | OCR | código ocr | ACTUAL | ai/enroll_face.py, ai/face_recognition.py (+más) | BAJO |
| `ocr/plate_recognition.py` | py | OCR | código ocr | LEGACY | ai/smartpark_demo_local.py | MEDIO |
| `ocr/requirements.txt` | txt | OCR | recurso ocr | ACTUAL | Sin mención estática; verificar | BAJO |
| `package-lock.json` | json | CONFIGURACIÓN | recurso configuración | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `package.json` | json | CONFIGURACIÓN | recurso configuración | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `probar_camaras.py` | py | TEST | código test | TEST | Sin mención estática; verificar | BAJO |
| `README.md` | md | CONFIGURACIÓN | recurso configuración | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `smartpark_edge_config.json` | json | CONFIGURACIÓN | recurso configuración | REQUIERE VERIFICACIÓN MANUAL | smartpark_edge_production.py | MEDIO |
| `smartpark_edge_installer/ai/bytetrack_smartpark.yaml` | yaml | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | ai/main.py, ai/smartpark_demo_local.py (+más) | MEDIO |
| `smartpark_edge_installer/build_smartpark_exe_v2.ps1` | ps1 | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | smartpark_edge_installer/crear_instalador_final.ps1, smartpark_edge_installer/crear_instalador_final_v2.ps1 | MEDIO |
| `smartpark_edge_installer/certs/camera/AmazonRootCA1.pem` | pem | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | mqtt_camera_test.py, smartpark_edge_config.json (+más) | MEDIO |
| `smartpark_edge_installer/certs/camera/camera-certificate.pem.crt` | crt | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | mqtt_camera_test.py, smartpark_edge_config.json (+más) | MEDIO |
| `smartpark_edge_installer/certs/camera/camera-private.pem.key` | key | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | mqtt_camera_test.py, smartpark_edge_config.json (+más) | ALTO |
| `smartpark_edge_installer/crear_instalador_final.ps1` | ps1 | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `smartpark_edge_installer/crear_instalador_final_v2.ps1` | ps1 | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `smartpark_edge_installer/crear_instalador_final_v3.ps1` | ps1 | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `smartpark_edge_installer/installer/output/SmartParkEdgeSetup.exe` | exe | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | smartpark_edge_installer/crear_instalador_final.ps1, smartpark_edge_installer/crear_instalador_final_v2.ps1 (+más) | MEDIO |
| `smartpark_edge_installer/installer/output/SmartParkEdgeSetup.rar` | rar | ARCHIVO HISTÓRICO | Paquete/build; no usar como fuente | ARCHIVO DE RESPALDO | Sin mención estática; verificar | MEDIO |
| `smartpark_edge_installer/models/smartpark/face_detection_yunet_2023mar.onnx` | onnx | MODELO | modelo inferencia | REQUIERE VERIFICACIÓN MANUAL | edge_server_demo_gpu_model_detection_v3.py, smartpark_edge_installer/build_smartpark_exe_v2.ps1 (+más) | MEDIO |
| `smartpark_edge_installer/models/smartpark/license_plate_yolov8n.pt` | pt | MODELO | modelo inferencia | REQUIERE VERIFICACIÓN MANUAL | edge_server_demo_gpu_model_detection_v3.py, smartpark_edge_installer/build_smartpark_exe_v2.ps1 (+más) | MEDIO |
| `smartpark_edge_installer/README_INSTALADOR_FINAL.txt` | txt | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `smartpark_edge_installer/README_SMARTPARK_V2.txt` | txt | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `smartpark_edge_installer/smartpark_edge.py` | py | EDGE | código edge | REQUIERE VERIFICACIÓN MANUAL | smartpark_edge_installer/build_smartpark_exe_v2.ps1, smartpark_edge_installer/smartpark_launcher_release_v2.py (+más) | MEDIO |
| `smartpark_edge_installer/smartpark_gate_cloud.py` | py | EDGE | código edge | PROBABLEMENTE ACTUAL | edge_server.py, edge_server_demo_gpu_model_detection_v3.py (+más) | BAJO |
| `smartpark_edge_installer/smartpark_launcher_release_v2.py` | py | EDGE | código edge | REQUIERE VERIFICACIÓN MANUAL | smartpark_edge_installer/build_smartpark_exe_v2.ps1, smartpark_edge_installer/SmartParkEdge_v2.spec | MEDIO |
| `smartpark_edge_installer/SmartParkEdge.iss` | iss | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | Sin mención estática; verificar | MEDIO |
| `smartpark_edge_installer/SmartParkEdge_Final.iss` | iss | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | smartpark_edge_installer/crear_instalador_final.ps1, smartpark_edge_installer/crear_instalador_final_v2.ps1 | MEDIO |
| `smartpark_edge_installer/SmartParkEdge_v2.spec` | spec | EDGE | recurso edge | REQUIERE VERIFICACIÓN MANUAL | smartpark_edge_installer/build_smartpark_exe_v2.ps1 | MEDIO |
| `smartpark_edge_installer/yolo11n.pt` | pt | MODELO | modelo inferencia | REQUIERE VERIFICACIÓN MANUAL | ai/smartpark_demo_local.py, ai/vehicle_detection.py (+más) | MEDIO |
| `smartpark_edge_production.py` | py | EDGE | código edge | PROBABLEMENTE ACTUAL | Sin mención estática; verificar | BAJO |
| `yolo11n.pt` | pt | MODELO | modelo inferencia | PROBABLEMENTE ACTUAL | ai/smartpark_demo_local.py, ai/vehicle_detection.py (+más) | BAJO |

## Alcance y vacíos

Se halló `entradav2 (1).ino` durante la verificación final; no estaba en el estado Git inicial. Importa `secrets.h`, ausente en el proyecto inspeccionado. Su versión funcional requiere verificación manual. Los ZIP/RAR/EXE no se ejecutaron ni extrajeron. La presencia de una ruta en esta tabla no autoriza incluirla en GitHub o en el ZIP final.
