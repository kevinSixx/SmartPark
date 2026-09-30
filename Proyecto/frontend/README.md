# Frontend SmartPark UCE

Aplicación React/Vite confirmada para el despliegue en AWS Amplify. Su código de interfaz permanece en `src/`, recursos en `public/`, pruebas en `tests/` y configuración en `vite.config.js`. La documentación de vistas existente está en `README_SMARTPARK_FRONTEND.md`.

## Configuración

`.env.example` contiene únicamente las tres variables que consume el código actual: `VITE_API_URL` (Backend), `VITE_EDGE_URL` (Edge local) y `VITE_EDGE_STREAM_URL` (flujo `/video`). Copiar el ejemplo a `.env` solo para trabajo local. Las variables `VITE_*` se incorporan al bundle del navegador; nunca poner secretos en ellas.

## Inicio y pruebas

Desde `Proyecto/frontend/`, con `node_modules` **ya existente**:

```powershell
npm run dev
npm run build
npm run lint
node --test tests/frontend-flows.test.js tests/openapi-contract.test.js
```

Este trabajo no ejecuta `npm install` ni `npm ci`, ni cambia `package.json`/`package-lock.json`. Vite usa normalmente el puerto 5173 en desarrollo; Backend escucha en 8000 y Edge en 9000 cuando están encendidos. El frontend consume rutas `/api/v1/` del Backend y `/health`, `/status`, `/video` del Edge. No inicia barrera, cámara ni servicios AWS por sí mismo.

## Errores frecuentes

Si falla el build por módulos faltantes, anotar el bloqueo; no instalar ni cambiar versiones en esta fase. Si la UI muestra error de red, comprobar `VITE_API_URL`, `VITE_EDGE_URL`, CORS y que los servicios locales estén iniciados. No subir `node_modules/`, `dist/`, `.env` ni ZIP previos.
