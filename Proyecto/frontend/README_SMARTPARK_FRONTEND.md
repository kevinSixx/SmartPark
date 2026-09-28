# SmartPark UCE - Frontend integrado

## Rutas

- `/login`: selector temporal de vista para desarrollo.
- `/admin`: panel administrativo.
- `/admin/users`: usuarios.
- `/admin/vehicles`: vehículos.
- `/admin/permissions`: permisos.
- `/admin/history`: historial.
- `/admin/access-test`: prueba manual de acceso existente.
- `/admin/staff`: interfaz preparada para cuentas ADMIN/GUARD.
- `/guard`: centro operativo Garita 01.
- `/guard/history`: historial visible para guardia.

## Arquitectura de la vista Guardia

La pantalla Guardia NO ejecuta YOLO ni ByteTrack en React.
Está preparada para consumir un servicio Edge local:

- `GET http://127.0.0.1:9000/health`
- `GET http://127.0.0.1:9000/status`
- `GET http://127.0.0.1:9000/video`

La URL puede cambiarse en `.env` mediante:

- `VITE_EDGE_URL`
- `VITE_EDGE_STREAM_URL`

El Backend AWS sigue configurado mediante `VITE_API_URL`.

## Estado actual

Ya funcionan con el Backend existente los módulos administrativos y la lectura del último historial en la vista Guardia.

Pendiente de la siguiente etapa:

- exponer `/health`, `/status` y `/video` desde el servicio Edge local;
- endpoints de apertura/cierre manual;
- tablas/cuentas de personal y autenticación real;
- auditoría de acciones de barrera.

El selector de rol de `/login` es únicamente una vista de desarrollo y no reemplaza la autenticación real.
