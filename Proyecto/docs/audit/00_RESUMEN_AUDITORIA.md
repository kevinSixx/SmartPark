# 00. Resumen ejecutivo de auditoría — SmartPark UCE

**Corte:** 2026-09-29. Solo inspección estática; no se ejecutaron servicios, cámaras, modelos, builds, migraciones ni AWS. Raíz Git `SmartPark/`, aplicación `Proyecto/`. Estado de Git tenía cambios previos en Frontend y `Proyecto/docs/` antes de esta auditoría. Las conclusiones «actual» describen rutas de código, no prueban que coincidan con el despliegue cloud o el EXE. [Inventario](01_INVENTARIO_COMPLETO.md) y [rutas](13_ENDPOINTS.md) contienen el detalle verificable.

| Pregunta | Respuesta basada en evidencia |
|---|---|
| 1. Versión actual funcional | Backend declara **1.7.2**, AI **2.8.1**, OCR **1.1.0**. Frontend fuente bajo `frontend/` tiene cambios locales no comprometidos. No se puede certificar el conjunto funcional sin pruebas y comparar AWS/Amplify/EXE. |
| 2. Edge canónico | **Candidato de fuente:** `smartpark_edge_production.py` → `edge_server_demo_gpu_model_detection_v3.py` → `smartpark_edge_installer/smartpark_gate_cloud.py`. El último está ignorado por Git. EXE usa otra copia `smartpark_edge_installer/smartpark_edge.py`; equivalencia requiere prueba manual. |
| 3. Backend canónico | `backend/app/main.py`, ocho routers y Dockerfile Backend. |
| 4. IA canónica | `ai/main.py`, Dockerfile AI; DeepFace es framework, ArcFace/RetinaFace son modelos/detector. |
| 5. OCR canónico | `ocr/main.py`, Dockerfile OCR; `ocr/plate_recognition.py` es otra implementación no importada por main. |
| 6. Frontend canónico | `frontend/src/main.jsx` → `App.jsx`, Vite en `frontend/package.json`; raíz `package.json` no inicia Vite. |
| 7. Docker/config usados | Tres Dockerfiles por servicio. Compose raíz solo DB+MQTT y tiene diferencia de mayúsculas en ruta Mosquitto; no constituye stack completo. Edge usa `smartpark_edge_config.json`; IA y Backend usan variables de entorno. |
| 8. Modelos obligatorios | Para flujo completo: YOLO11n, YuNet, detector YOLOv8n de placa, ArcFace/RetinaFace y PaddleOCR. Los tres primeros están en fuente y duplicados en instalador; DeepFace/Paddle caches no están empaquetados como fuente. |
| 9. Redundancias claras | Copias bit a bit de tres modelos y clave IoT, ZIP/RAR de múltiples fechas, `node_modules`, `.venv`, cachés y builds. No afirmar que demos/instalador carecen de uso. |
| 10. Archivos de riesgo | `.env`, `frontend/.env`, clave y certificado IoT, fotos/embedding personales, instalador con copia de clave, config con endpoints y dependencias del Edge ignoradas. |
| 11. Secretos antes de GitHub | Revocar/rotar IoT mTLS y revisar/rotar JWT, DB y credenciales asociadas. `.env` y clave privada ya están en Git: `.gitignore` no basta; sanear historial en etapa autorizada. No publicar biometría personal. |
| 12. Dependencias mezcladas | Edge no tiene requirements propios; AI contiene OCR de demo que importa PaddleOCR sin declararlo, `boto3` AI y `paho-mqtt` Backend parecen no tener import directo; root npm duplica parte del Frontend. Versiones sin pin reducen reproducibilidad. |
| 13. Pruebas locales | OCR, AI health/ready, Backend con PostgreSQL local, Vite, cámara/Edge demo y contratos HTTP con muestras consentidas. Ver [plan](14_PLAN_PRUEBAS_LOCAL.md). |
| 14. Pruebas con AWS | MQTT/TLS real ESP32–IoT–Edge, S3, RDS/ALB/ASG/API Gateway/Amplify y barrera end to end desplegada. |
| 15. ZIP final | Fuente depurada por módulo, manifiestos/lock, modelos solo si redistribución permitida, ejemplos sin secretos, docs y pruebas, `VERSION`, hashes/licencias. Incluir `entradav2 (1).ino` solo tras compilarlo, verificar su versión y completar una plantilla segura de `secrets.h`. |
| 16. Fuera del ZIP | `.venv`, `node_modules`, cachés, builds/archives redundantes, claves/certs de dispositivo, `.env` reales, fotos/embeddings personales, ejecutable antiguo sin revisión. |
| 17. Faltantes de reproducción | El firmware `entradav2 (1).ino` apareció durante la auditoría, pero falta `secrets.h`, compilación/versión confirmada y librerías; además núcleo Edge versionado y requirements, `.env.example` útiles, Compose local completo, origen/licencia/hash de modelos, provisión AWS/IAM, muestras anonimizadas, build limpio y prueba end to end. |
| 18. Orden de reorganización | IoT → Edge → Backend → AI → OCR → Frontend → Infra → Docs → Tests → limpieza; cada fase con commit, prueba mínima y rollback. [Plan detallado](18_PLAN_REORGANIZACION.md). |

## Riesgos prioritarios

1. **Crítico:** clave privada IoT y `.env` versionados; duplicado de clave en instalador. Rotar y sanear antes de publicar.
2. **Crítico para reproducibilidad:** núcleo `smartpark_gate_cloud.py` ignorado y ausente de la raíz de imports; el firmware encontrado necesita `secrets.h` ausente y validación de versión.
3. **Alto:** rutas Backend internas y CRUD sin dependencia JWT visible; revisar controles de API Gateway/ALB y permisos.
4. **Alto:** Compose incompleto, hostname OCR solo válido en red Docker configurada, y build AI depende de precarga de modelos.
5. **Alto:** no hay prueba de correspondencia entre fuente, EXE Edge y versiones cloud/Amplify; no usar nombres `production`, `v3`, `final` como prueba.

## Verificación manual pendiente

- ¿Es `entradav2 (1).ino` la versión ESP32 entregada? Confirmar compilación, librerías, `secrets.h` provisionado fuera de Git y comportamiento físico. El código observado usa TRIG 5, ECHO 18, servo 19, umbral 20 cm, MQTT/TLS y comandos OPEN/CLOSE; los topics coinciden textualmente con defaults Edge/Backend.
- ¿Qué commit/artefacto está desplegado en Amplify, Backend ASG, AI ASG y OCR, y con qué tags/digests ECR?
- ¿Qué rama Edge se ejecutó en la demostración final: Python de raíz o `SmartParkEdgeSetup.exe`? ¿En qué PC y con qué cámara?
- ¿El OCR corre como contenedor `smartpark_ocr` junto a AI, en otro host o por red externa? Confirmar `OCR_SERVICE_URL` real.
- ¿Cuáles son las licencias y fuentes de los pesos, y hay permiso de redistribución?
- ¿Se aplicaron todas las revisiones Alembic a RDS y qué controles protegen `/access/authorize` y `/face-profiles/match`?
- ¿Qué datos biométricos cuentan con consentimiento y cuáles deben retirarse del historial Git?
