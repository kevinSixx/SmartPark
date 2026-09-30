# 15. Legacy, redundancias y entregables

«NO ENTREGAR» se refiere al ZIP/GitHub final futuro; no se borró nada. La clasificación no equivale a ausencia de uso.

| Elemento | Clasificación | Evidencia y condición |
|---|---|---|
| `entradav2 (1).ino` | REQUIERE VERIFICACIÓN; posible firmware a MANTENER | Apareció sin seguimiento Git durante auditoría; incluye HC-SR04/SG90 y MQTT/TLS, pero `secrets.h` falta y no se compiló. El nombre no prueba vigencia |
| `.venv/`, `node_modules/` raíz y Frontend, `__pycache__/`, `.pytest_cache/` | NO ENTREGAR | Dependencias/cachés generados localmente; reconstruir desde manifiestos |
| `frontend/dist/`, `frontend/smartpark-amplify/`, `smartpark_edge_installer/build/`, `dist/` | NO ENTREGAR en fuente; ARCHIVAR si se exige evidencia de despliegue | Builds reproducibles en principio; comparar versión con fuente y registrar hashes |
| `ai.zip`, `frontend.zip`, `frontend.rar`, `frontend/smartpark-amplify*.zip` | ARCHIVAR; NO ENTREGAR en ZIP fuente | Instantáneas distintas, algunas modificadas localmente; no asumir que «v4» es vigente sin fecha/hash/despliegue Amplify |
| `smartpark_edge_installer/installer/output/SmartParkEdgeSetup.exe/.rar` | REQUIERE VERIFICACIÓN; no publicar ahora | Instalador distribuible con modelos y copia de certificados/clave; revisar contenido y procedencia antes de entrega |
| `edge_server.py` | ARCHIVAR provisionalmente | API anterior; import del núcleo, sin llamada desde launcher encontrado |
| `edge_server_demo_gpu_model_detection_v3.py` | MANTENER | Aunque dice demo, es import directo del lanzador de producción |
| `smartpark_edge_production.py` | MANTENER como candidato | Configura núcleo real y retira `/demo/trigger` |
| `smartpark_edge_installer/smartpark_edge.py`, `smartpark_launcher_release_v2.py`, `.spec`, `.iss`, scripts `.ps1` | REQUIERE VERIFICACIÓN | Fuente de EXE, ignorada por Git; comparar con rama de fuente y decidir si mantener módulo de packaging |
| `smartpark_edge_installer/smartpark_gate_cloud.py` | MANTENER después de saneamiento | Núcleo compartido real; su exclusión de Git impide clon reproducible |
| Tres modelos duplicados en instalador | ARCHIVAR copias; mantener una fuente canónica | SHA-256 coincide por cada par; licencias pendientes |
| Certificados/clave duplicados | NO ENTREGAR | La clave privada idéntica está en dos ubicaciones; revocar y reemplazar |
| `ai/plate_recognition.py`, `ocr/plate_recognition.py`, demos/scripts de cámara | REQUIERE VERIFICACIÓN | OCR principal usa `ocr/main.py`; los otros módulos pueden servir demo/prueba y no se deben borrar por búsqueda de imports |
| `ai/faces/`, `ai/debug_*`, `ai/faces/kevin_embedding.npy` | NO ENTREGAR | Datos biométricos personales; reemplazar por datos consentidos/anonimizados |
| `package.json` y `node_modules/` de raíz | ARCHIVAR tras confirmar historial | No contienen scripts Vite; Frontend real vive en `frontend/` |

Para decidir vigencia de cada archivo histórico: comparar hash y diff, revisar scripts/subprocess, referencia Docker, rutas HTTP/MQTT, Git log y **despliegue efectivo** con el responsable. No abrir ZIP/RAR/EXE ni ejecutar instaladores en esta auditoría.
