# Acciones de seguridad antes de GitHub público

La auditoría encontró material sensible previamente versionado bajo `Proyecto/`: `.env` de raíz y Frontend, clave privada y certificado IoT, fotos/embedding faciales y capturas de depuración. Estos archivos se retiraron del índice con `git rm --cached`; los `.env`, datos faciales y capturas locales permanecen en disco, y las copias privadas bajo `edge/certs/` y `smartpark_edge_installer/certs/` siguen ignoradas. Los objetos de commits anteriores todavía contienen el material sensible. Los ZIP/RAR/EXE/build históricos deben tratarse como respaldos no distribuidos. `.gitignore` y el retiro del índice no limpian el historial.

Acciones manuales obligatorias, con autorización del responsable:

1. Rotar/revocar el certificado y clave mTLS IoT expuestos; emitir un par nuevo y revisar policy/client ID.
2. Revisar y rotar, si eran reales, la contraseña DB/RDS y `AUTH_SECRET_KEY` JWT; invalidar tokens cuando proceda.
3. Verificar que `node_modules/`, artefactos de frontend y otros archivos generados retirados del índice no vuelvan a prepararse; sanear el historial Git antes de repositorio público. Planificar consecuencias para clones y colaboradores; **no** se ejecutó `git filter-repo`.
4. Auditar ZIP/RAR/EXE y capturas antiguas antes de entregar; pueden contener la clave, `.env` o datos personales.
5. Confirmar protección de `/access/authorize`, `/face-profiles/match` y otras rutas sin JWT visible en Backend/API Gateway/ALB antes de exposición pública.

No se revocó nada ni se modificó AWS. Antes de publicar, verificar de nuevo `git ls-files` y escanear todo el historial, incluidos los objetos de archivos eliminados. No publicar ni generar un ZIP desde `Proyecto/` mientras estén pendientes esas acciones.
