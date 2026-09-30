# 11. Configuración y secretos

Inspección sin imprimir valores. Detección por nombres y formato PEM; algunas coincidencias de `password`/`token` en código son variables, no credenciales literales. **Git ya sigue secretos reales:** `Proyecto/.env`, `Proyecto/frontend/.env` y `Proyecto/certs/camera/camera-private.pem.key` figuran en `git ls-files`. Ignorar ahora no elimina historial; antes de GitHub se deben revocar/rotar credenciales y planificar saneamiento del historial en una etapa autorizada.

| Archivo | Tipo | Riesgo | Acción futura recomendada |
|---|---|---|---|
| `.env` | `DATABASE_URL`, `AUTH_SECRET_KEY`, bucket, región y URL AI | ALTO; versionado | Rotar DB/JWT si valores reales; sacar de Git e historial, crear `.env.example` sin valores (el actual está vacío) |
| `frontend/.env` | `VITE_API_URL`, `VITE_EDGE_URL`, `VITE_EDGE_STREAM_URL`, `VITE_DEMO_AUTH` | MEDIO; versionado y embebido en build | Tratar `VITE_*` como públicos; revisar URL/modo demo, crear example y no poner secretos allí |
| `certs/camera/camera-private.pem.key` | Clave privada mTLS IoT | CRÍTICO; versionada | Revocar certificado IoT asociado y emitir par nuevo fuera de repo; purgar historial antes de publicar |
| `certs/camera/camera-certificate.pem.crt` | Certificado cliente | ALTO por asociación a clave | Reemitir junto con clave; documentar provisión segura |
| `certs/camera/AmazonRootCA1.pem` | CA pública | BAJO | Se puede incluir si licencia/procedencia se confirma; no es secreto |
| `smartpark_edge_installer/certs/camera/` | Copia exacta de clave/certificados | CRÍTICO; ignorada pero puede ir en ZIP/EXE | Nunca entregar copia ni ejecutable que la contenga; reconstruir tras rotación |
| `smartpark_edge_config.json` | Rutas de certificados, URL, topic, cliente/cámara | MEDIO | Convertir a plantilla sin datos de cuenta/host sensible; usar configuración local fuera de Git |
| `docker-compose.yml` | Password DB de desarrollo en claro | MEDIO | Sustituir por variable/secret en Compose futuro; no reutilizar en RDS |
| `entradav2 (1).ino` / `secrets.h` ausente | Referencias a Wi-Fi, endpoint IoT, CA, certificado y clave privada | ALTO si se entrega `secrets.h` real | Mantener `secrets.h` fuera de Git; proporcionar solo plantilla de nombres y aprovisionamiento |
| `ai/faces/`, `ai/debug_*` | Fotos/embedding biométricos | ALTO; fotos versionadas | Retirar de publicación/ZIP y usar muestras anonimizadas con consentimiento |
| Scripts Backend `create_admin.py`, modelos de schema/auth | Variables llamadas password/token | REVISAR; coincidencia léxica | Revisar literales/manual de provisión; el escaneo no demuestra credenciales reales |

No se halló patrón inequívoco de AWS access key ID en archivos de aplicación inspeccionados. Eso no prueba ausencia en binarios, ZIP/RAR, historial o servicios remotos. No se abrieron valores secretos en el informe.

## Propuesta de `.gitignore` final (sin aplicar)

Ignorar `**/.env`, `**/.env.local`, `**/.venv/`, `**/node_modules/`, `**/__pycache__/`, `**/.pytest_cache/`, `**/dist/`, `**/build/`, `*.pyc`, `*.key`, `*.pem.key`, `certs/**/camera-certificate.pem.crt`, `**/faces/`, `**/debug_*.jpg`, `*.zip`, `*.rar`, `*.exe`, `*.npy` biométricos. Permitir expresamente `**/.env.example` y fuentes del futuro instalador/Edge tras revisar licencias. No ignorar de manera indiscriminada `smartpark_edge_installer/` si contiene el único núcleo requerido. Un `.gitignore` por sí solo no protege archivos ya versionados.
