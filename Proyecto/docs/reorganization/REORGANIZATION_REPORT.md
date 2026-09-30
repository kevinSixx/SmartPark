# Informe de reorganización — 2026-09-29

## 1. Árbol anterior y 2. árbol nuevo

El árbol anterior estaba bajo `Proyecto/` con módulos activos mezclados con firmware, Edge, pesos, instalador ignorado, `.env`, certificados, fotos, ZIP/RAR/builds. Ver [BEFORE_TREE.txt](BEFORE_TREE.txt), [BEFORE_GIT_STATUS.txt](BEFORE_GIT_STATUS.txt) y [inventario completo](../audit/01_INVENTARIO_COMPLETO.md); `BEFORE_TREE` fue generado con `rg --files` y omite parte de los archivos ignorados del instalador, que sí están en la auditoría.

El árbol nuevo en la raíz Git es `firmware/`, `edge/`, `backend/`, `ai/`, `ocr/`, `frontend/`, `infra/`, `docs/`, `tests/`, `sample-data/`, más Compose, README, VERSION y manifiesto. `Proyecto/` queda como respaldo local ignorado, no como fuente entregable. Ver [AFTER_TREE.txt](AFTER_TREE.txt).

## 3. Archivos movidos y 4. renombrados

- `Proyecto/backend/`, `ai/`, `ocr/`, `frontend/`, `docs/` → carpetas homónimas de raíz, conservando código interno y cambios Frontend preexistentes.
- `entradav2 (1).ino` → `firmware/esp32/SmartParkUCE.ino`; no se editó su lógica.
- Launcher Edge, servidor V3 y núcleo de instalador → `edge/app/`, conservando nombres para trazabilidad. `edge_server.py` → `edge/legacy/`.
- Tres pesos → `edge/models/`; copias idénticas del instalador permanecen en respaldo ignorado. YAML ByteTrack AI copiado a `edge/app/` sin retirar el de AI.
- `.py`, `.ps1`, `.spec`, `.iss`, `.txt` del instalador → `edge/installer/`; antigua copia del servidor quedó en `Proyecto/smartpark_edge_installer/`; el archivo publicable `smartpark_edge.py` es adaptador.
- `mosquitto/mosquitto.conf` queda en la raíz `Proyecto/` como configuración funcional del broker; Compose monta esa ruta.
- `.env`/certificados personales, `ai/faces/` y fotos debug → `Proyecto/local-private/` ignorado. `frontend/node_modules/`, `dist/`, build Amplify y ZIP históricos → `Proyecto/archive/frontend/` ignorado. No se borraron respaldos.

## 5. Imports y 6. paths modificados

Imports Edge cambiados a `edge.app` y `edge.installer`; módulos `__init__.py` añadidos. `gate` resuelve YOLO y tracker en `edge/models`/`edge/app`; el servidor V3 resuelve YuNet y placa en `edge/models`; launcher permite `SMARTPARK_EDGE_CONFIG` privado y rutas de cert bajo `edge/certs`. GUI usa modelos/código canónicos y certificados externos en LocalAppData. AI local busca peso en `edge/models` y conserva fallback `/app/yolo11n.pt` para su imagen; `ai/Dockerfile` copia desde el nuevo origen. No se alteraron thresholds, endpoints, topics, payloads ni puertos.

## 7. Archivos no tocados y 8. legacy conservado

No se editaron `backend/app/`, `backend/migrations/`, `backend/tests/`, `ai/main.py`, `ocr/main.py`, `ocr/Dockerfile`, ni UI/lógica Frontend. Solo cambió el scope de ESLint para excluir un build histórico. `ai/plate_recognition.py`, `ocr/plate_recognition.py`, demos AI y Edge anterior quedan para revisión. No se tocaron configuraciones AWS desplegadas.

## 9. Secretos excluidos

La fuente nueva contiene examples sin valores secretos. Clave/certificados originales, `.env`, biometría y ejecutables históricos se mantienen en respaldo ignorado y **siguen existiendo en el historial Git anterior**. Ver [SECURITY_ACTIONS_REQUIRED.md](SECURITY_ACTIONS_REQUIRED.md). No se rotó ni saneó el historial.

## 10. Pruebas ejecutadas y 11. fallidas

Pasaron compileall, 3 tests estructurales, 15 tests Frontend, build Vite y `docker compose config -q`; los hashes de los tres pesos coinciden con antes. `npm run lint` falla con seis reglas de hooks de código previo. `docker info` falla por daemon inactivo. Python global no tiene `pytest` ni paquetes de servicios; no se iniciaron los cinco servidores, no se construyeron imágenes ni se probó firmware/EXE. Detalle en [LOCAL_TEST_REPORT.md](../testing/LOCAL_TEST_REPORT.md).

## 12. AWS, 13. Edge y 14. Docker

Pruebas AWS pendientes en [AWS_TESTS_PENDING.md](../testing/AWS_TESTS_PENDING.md). La comparación, decisión y límites de Edge están en [EDGE_DECISION.md](EDGE_DECISION.md). Compose es local con DB, Backend, AI y OCR; Mosquitto opcional; tres Dockerfiles siguen separados con contextos explícitos. No se desplegó ni publicó nada.

## 15. Riesgos restantes

Seguridad e historial impiden GitHub público ahora; licencia/origen de pesos sin confirmar; startup local/cámara/MQTT/EXE sin prueba; Docker daemon inactivo; DB local sin esquema; correspondencia con Amplify/ECR/ASG no verificada; linter Frontend pendiente. `git diff` de movimientos sin staging muestra principalmente eliminaciones antiguas; revisar el estado completo y preparar staging cuidadosamente después de sanear secretos. No hacer ZIP desde el directorio completo antes de cerrar estas puertas.
