# Informe de pruebas locales — 2026-09-29

No se tocaron AWS, RDS, S3, IoT ni barrera física. Los tests de Backend existentes usan `engine.connect()` y escriben dentro de una transacción; se reservaron para una DB local desechable. El Python global no tiene las dependencias de servicios y el daemon Docker Desktop no estaba activo.

| Componente | Comando | Resultado | PASS/FAIL | Error o límite | Siguiente acción |
|---|---|---|---|---|---|
| Python Edge/Backend/AI/OCR | `python -m compileall -q edge backend ai ocr tests` | Sintaxis compila | PASS | No importa modelos ni levanta apps | Prueba de import/startup en entorno aislado |
| Spec/JSON Edge | `python -m py_compile edge/installer/SmartParkEdge_v2.spec`; parse JSON example | Sintaxis y JSON válidos | PASS | No ejecuta PyInstaller | Build Windows en PC aislada |
| Contratos estructurales | `python -m unittest discover -s tests -v` | 3/3 pasan; pesos, rutas Edge, firmware y spec | PASS | Prueba estática | Probar hardware y red local |
| Enlaces de documentación nueva | Verificación de rutas Markdown locales | 0 enlaces rotos | PASS | No valida contenido externo/AWS | Revisar capturas y enlaces finales del PDF |
| Frontend contratos | `node --test` desde `frontend/` | 15/15 pasan | PASS | Sin navegador real | Navegar con Backend/Edge de prueba |
| Frontend build | `npm run build` desde `frontend/` | Vite 8.3.1, 1.913 módulos, build correcto | PASS | No prueba Amplify | Validar build/config de Amplify sin desplegar |
| Frontend lint | `npm run lint`; después `eslint . --format json` con build histórico ignorado | Primer pase: 274 errores incluyendo bundle generado; segundo: 6 errores de fuente | FAIL | `react-hooks/set-state-in-effect` en AccessHistory, GuardGate, Permissions, Staff, Users y Vehicles | Corregir en trabajo funcional separado con pruebas UI |
| Compose configuración | `docker compose config -q` con placeholders locales | YAML y variables válidos | PASS | No prueba imágenes | Arrancar Docker Desktop y usar proyecto/volumen aislado |
| Docker daemon | `docker info` | No conecta a pipe `dockerDesktopLinuxEngine` | FAIL | Daemon no activo | Iniciar Docker Desktop; build con `-p`/proyecto de prueba aislado |
| Backend tests existentes | `python -m pytest --collect-only -q backend/tests` | No inicia | FAIL | Python global no tiene `pytest`; los fixtures precisan PostgreSQL | Instalar dependencias en entorno aislado y DB local; nunca usar RDS |
| OCR :8002 | `uvicorn ocr.main:app --port 8002` | No ejecutado | PENDIENTE | Falta PaddleOCR/uvicorn en Python global y Docker daemon | Instalar/build local y probar `/health`, `/plate` con muestra consentida |
| AI :8001 | `uvicorn ai.main:app --port 8001` | No ejecutado | PENDIENTE | Faltan DeepFace, Ultralytics, uvicorn y OCR local | Probar `/health`, `/ready`, `/process` en stack aislado |
| Backend :8000 | `uvicorn backend.app.main:app --port 8000` | No ejecutado | PENDIENTE | Faltan FastAPI/SQLAlchemy/DB y secreto local | DB desechable, `/health`, `/db-check`, tests transaccionales |
| Frontend dev | `npm run dev` | No ejecutado | PENDIENTE | Backend/Edge no activos; build/test ya pasaron | Abrir Vite con servicios locales |
| Edge :9000 | `python -m edge.app.smartpark_edge_production` | No ejecutado | PENDIENTE | Faltan paquetes/cámara/certificados nuevos; iniciar conecta MQTT real | PC de prueba, comprobar `/health`, `/status`, `/video` y POST local autorizado |
| ESP32 | `arduino-cli version`; luego compilar y cargar `SmartParkUCE.ino` | CLI no encontrada; compilación no ejecutada | PENDIENTE | Falta Arduino CLI, `secrets.h`, core/FQBN confirmado y placa de prueba | Instalar toolchain, compilar offline; prueba física manual autorizada |
| Instalador | `build_smartpark_exe_v2.ps1` | No ejecutado | PENDIENTE | PyInstaller/Inno y PC Windows limpia pendientes | Verificar EXE sin clave embebida y rutas/modelos |

El test `node --test` y el build se hicieron antes de archivar `frontend/node_modules/` en `Proyecto/archive/frontend/`. Para repetirlos, ejecutar `npm ci` dentro de `frontend/`. No hay afirmación de PASS para servicios no iniciados.
