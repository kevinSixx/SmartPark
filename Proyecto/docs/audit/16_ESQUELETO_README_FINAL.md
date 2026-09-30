# 16. Esqueleto propuesto del README final

No sustituye `README.md`. Cada sección debe redactarse solo tras validar el despliegue y licencias.

```markdown
# SmartPark UCE
Descripción breve del problema, alcance y estado de validación.

## Arquitectura
Diagrama de ESP32 → AWS IoT → Edge → API Gateway → Backend → IA → OCR,
RDS/S3/IoT → barrera y Frontend Amplify. Diferenciar local de AWS.

## Componentes y estructura
firmware/, edge/, backend/, ai/, ocr/, frontend/, infra/, docs/, tests/.

## Requisitos
Python/Node/Docker compatibles, Windows/cámara para Edge, recursos mínimos,
cuenta AWS solo para integración cloud.

## Hardware
ESP32, HC-SR04, SG90, cámara/DroidCam, cableado y pinout verificado.
Confirmar si `entradav2 (1).ino` es la versión final; documentar `secrets.h`
como archivo privado y ofrecer solo una plantilla segura.

## Instalación
Clonado limpio, dependencias por módulo, migraciones solo en DB nueva,
modelo/pesos con hash y licencias, build Frontend.

## Configuración y variables de entorno
Tablas por módulo, ejemplos sin secretos, política de rotación, URL local/cloud.

## Modelos
YOLO11n, YuNet, detector de placa, ArcFace/RetinaFace, PaddleOCR:
origen, versión, tamaño, hash, licencia, descarga/caché.

## Docker y ejecución local
Compose propuesto, perfil PostgreSQL, comandos por servicio, health/ready,
modo CPU y modo cámara/sensor de prueba.

## Ejecución AWS
Amplify, API Gateway, ALB/ASG, EC2/ECR, RDS, S3, IoT Core;
diagrama y permisos, sin IDs ni claves privadas.

## Pruebas y endpoints
Matriz local/AWS, comandos y resultados esperados; enlace a OpenAPI
actualizado y decisiones AUTHORIZED/REJECTED.

## IoT
Topics y payloads reales, aprovisionamiento, mTLS, reconexión, seguridad.

## Seguridad y limitaciones
JWT por ruta, CORS, IAM, biometría/consentimiento, resiliencia,
latencias y fallos conocidos.

## Autores y licencia
Créditos académicos, fecha/versión y licencias propias/de terceros confirmadas.
```

Antes de publicar, el README debe declarar claramente qué elementos de AWS son prerrequisitos externos y qué parte corre sin AWS. No incluir capturas con datos personales o endpoints privados que faciliten acceso no autorizado.
