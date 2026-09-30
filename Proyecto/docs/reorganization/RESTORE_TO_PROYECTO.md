# Restauración de la raíz funcional — 2026-09-30

**Raíz funcional actual: `SmartPark/Proyecto/`.** Los documentos anteriores de esta carpeta describen la reorganización externa del 2026-09-29 y quedan como registro histórico; no describen la ubicación operativa actual.

## Recuperación realizada

- Se devolvieron `backend/`, `ai/`, `ocr/`, `frontend/`, `docs/`, el firmware `entradav2 (1).ino`, los tres pesos, `models/`, Mosquitto y `docker-compose.yml` a `Proyecto/`.
- Se restablecieron las rutas y nombres Edge originales: `smartpark_edge_production.py`, `edge_server_demo_gpu_model_detection_v3.py`, `edge_server.py`, `smartpark_edge_installer/` y `smartpark_edge_config.json`. El servidor V3 recuperado coincide con el SHA-256 original registrado antes de reorganizar: `6203B554F79CD9B13DCF7965C2A2C16340F90AA22092996B3424ADE3AFE63B0A`.
- Se recuperaron `.env`, `.env` Frontend, certificados, fotos/embedding locales, `node_modules`, build Amplify y ZIP históricos a sus rutas anteriores, sin imprimir valores.
- `Proyecto/.venv/` nunca se movió ni se recreó. No se instalaron paquetes.
- Los archivos externos de la reorganización están preservados en `SmartPark/_reorganization_backup/`. La `.gitignore` de la raíz Git permanece únicamente para excluir ese respaldo y archivos sensibles; no define la raíz de ejecución.

## Comprobaciones de contenido

`git diff --name-status` no reporta cambios en Backend, AI, OCR ni Compose respecto al estado versionado original. Los `requirements.txt`, Dockerfiles y entrypoints principales coinciden en contenido con `HEAD:Proyecto/...`. Los cambios Frontend que ya estaban antes de la reorganización se conservaron. El firmware conserva SHA-256 `01C1FCA86919C10B553719D2B5A7481CDCDB2F5D06CA4666A104DEFC1310B367`. Los pesos conservan los tres hashes de [MODEL_HASHES_BEFORE.md](MODEL_HASHES_BEFORE.md). La copia histórica `smartpark_edge_installer/smartpark_edge.py` conserva SHA-256 `95B4DF418C3FEE902E7D2355D453DFFC5B368EB943D71`.

Una comparación de los **31 archivos** de `frontend/src/` con la copia externa archivada dio cero diferencias. Existen los 14 destinos funcionales comprobados, incluido `Proyecto/.venv/Scripts/python.exe`. El núcleo Edge, launcher GUI, spec y script de build recuperaron los tamaños observados antes de la reorganización (44.654, 20.226, 4.883 y 2.220 bytes respectivamente); el servidor V3 y los tres pesos sí tienen hashes anteriores verificados.

El núcleo Edge, launcher GUI y spec del instalador original estaban ignorados por Git; se revirtieron los cambios conocidos de la reorganización, pero no existe un hash anterior de esos tres archivos para certificar igualdad byte a byte. No se ejecutaron servicios, cámara ni instalador en esta restauración.

## Documentación conservada en `Proyecto/docs/`

Se copiaron los 20 archivos de `audit/`, la instantánea `smartpark-openapi-production.json`, `reorganization/` (inventarios antes/después, hashes, decisión Edge, seguridad e informe histórico), `testing/` (pruebas locales y AWS pendientes), `evidence/README.md`, y los README de `api/`, `architecture/`, `costs/` e `installation/`. Los README y examples de módulo creados para el árbol externo se guardaron en `_reorganization_backup/copied_into_project/` porque sus rutas podían inducir a error en la estructura restaurada.

## Límites

La recuperación fue de archivos y rutas. No se hizo `pip install`, `npm install`, Docker build, llamada AWS, despliegue, `git push` ni prueba funcional. No se tocó `.git/`. Los secretos históricos siguen requiriendo tratamiento separado antes de una publicación pública.
