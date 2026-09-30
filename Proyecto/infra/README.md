# Infraestructura

## Docker local

`Proyecto/docker-compose.yml` permanece en la raíz y actualmente define **solo PostgreSQL `db` (5432) y Mosquitto `mqtt` (1883)**. No es una réplica del despliegue AWS ni inicia Backend, IA, OCR, Edge o Frontend. Usa una contraseña de desarrollo escrita en el Compose original; revisar antes de compartirlo y no reutilizarla en cloud. `mosquitto/mosquitto.conf` es configuración funcional del broker (`listener` y acceso anónimo), por lo que se conserva. El volumen MQTT indica `./mosquitto/mosquitto.conf`, con la misma capitalización que la carpeta. La ruta se corrigió sin cambiar puertos, tópicos ni comportamiento del broker.

Los Dockerfiles existentes se identifican por servicio: `backend/Dockerfile` y `ai/Dockerfile` usan contexto `Proyecto/`; `ocr/Dockerfile` usa contexto `Proyecto/ocr/`. Los comandos de build están documentados en los README de cada módulo y **no se ejecutaron** en esta fase.

## AWS desplegado

El despliegue descrito en la auditoría incluye Frontend en **Amplify**, entrada **API Gateway**, Backend detrás de **ALB** y **ASG**, IA detrás de ALB interno y ASG, datos en **RDS** y **S3**, imágenes en **ECR** e integración de ESP32/Edge mediante **IoT Core**. Esta carpeta es documentación: no contiene una plantilla de infraestructura que recree AWS. Revisar `docs/audit/` y obtener diagramas/capturas autorizados para el informe. No se ejecutó AWS CLI ni ningún despliegue.
