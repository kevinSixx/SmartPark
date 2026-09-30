# SmartPark UCE

Sistema académico de **control de acceso vehicular inteligente** desarrollado para la **Universidad Central del Ecuador**. SmartPark integra **IoT, Edge Computing, visión artificial, servicios web y arquitectura cloud en AWS** para detectar vehículos, reconocer al conductor, leer la placa, validar permisos y controlar una barrera física.

> Proyecto integrador académico. La solución combina procesamiento local en la garita con servicios desplegados en AWS.

---

## Integrantes

- **Kevin Vladimir Rueda Chavarría**
- **Damián Cesar Ferri Donoso**
- **Neiser Fabián Azas Poaquiza**

**Universidad Central del Ecuador**  
Carrera de Ingeniería en Sistemas de Información

---

## Tabla de contenido

1. [Descripción general](#descripción-general)
2. [Problema que resuelve](#problema-que-resuelve)
3. [Objetivo](#objetivo)
4. [Arquitectura general](#arquitectura-general)
5. [Flujo de funcionamiento](#flujo-de-funcionamiento)
6. [Tecnologías principales](#tecnologías-principales)
7. [Estructura del repositorio](#estructura-del-repositorio)
8. [Componentes del sistema](#componentes-del-sistema)
9. [Edge Computing](#edge-computing)
10. [IoT y MQTT](#iot-y-mqtt)
11. [Inteligencia artificial y visión artificial](#inteligencia-artificial-y-visión-artificial)
12. [Backend](#backend)
13. [Frontend](#frontend)
14. [Infraestructura AWS](#infraestructura-aws)
15. [Base de datos](#base-de-datos)
16. [Almacenamiento de evidencias](#almacenamiento-de-evidencias)
17. [Endpoints y servicios](#endpoints-y-servicios)
18. [Ejecución local](#ejecución-local)
19. [Despliegue](#despliegue)
20. [Seguridad](#seguridad)
21. [Pruebas realizadas](#pruebas-realizadas)
22. [Limitaciones y mejoras futuras](#limitaciones-y-mejoras-futuras)

---

## Descripción general

**SmartPark UCE** es una plataforma para automatizar y supervisar el acceso de vehículos a una garita universitaria.

El sistema utiliza una cámara y sensores conectados a un equipo Edge para detectar la llegada de un vehículo. A partir de ese evento se realiza captura de evidencia, reconocimiento facial, lectura de placa y consulta de permisos. La decisión final se registra en la nube y puede activar una barrera mediante un dispositivo ESP32 conectado a **AWS IoT Core**.

La plataforma dispone además de una interfaz web para administración y operación de la garita, donde se pueden gestionar:

- usuarios;
- vehículos;
- permisos;
- perfiles faciales;
- historial de accesos;
- auditoría de acciones de barrera;
- personal administrativo y guardias;
- pruebas de acceso;
- estado del sistema.

---

## Problema que resuelve

En un esquema de acceso vehicular manual, la validación de identidad, placa y autorización depende de la intervención humana, lo que puede provocar demoras, inconsistencias y poca trazabilidad.

SmartPark propone un flujo automatizado en el que:

1. se detecta físicamente la presencia del vehículo;
2. se captura el rostro del conductor;
3. se captura y reconoce la placa;
4. se consulta la información almacenada;
5. se valida el permiso vigente;
6. se registra el evento;
7. se envía una orden de apertura o cierre de barrera.

---

## Objetivo

Diseñar e implementar un prototipo funcional de control de acceso vehicular que integre **IoT, Edge Computing, inteligencia artificial y servicios cloud en AWS**, manteniendo trazabilidad de los accesos y permitiendo supervisión desde una interfaz web.

---

## Arquitectura general

La arquitectura está dividida en dos zonas principales:

### Garita / entorno local

- cámara conectada al equipo Edge;
- procesamiento de video con OpenCV;
- detección y seguimiento con YOLO + ByteTrack;
- selección del mejor frame;
- captura de rostro y placa;
- ESP32;
- sensor ultrasónico HC-SR04;
- microservo SG90;
- API local del Edge.

### AWS Cloud

- AWS Amplify;
- API Gateway;
- Application Load Balancer;
- Auto Scaling Groups;
- EC2;
- Amazon ECR;
- Amazon RDS PostgreSQL;
- Amazon S3;
- AWS IoT Core.

Flujo resumido:

```text
Cámara / Sensor
      |
      v
Edge local
      |
      | HTTPS
      v
API Gateway
      |
      v
Backend AWS
      |
      +------> RDS PostgreSQL
      |
      +------> S3
      |
      +------> IA / OCR
      |
      +------> AWS IoT Core
                     |
                     v
                   ESP32
                     |
                 SG90 / Barrera
```

### Principio de diseño

Las imágenes y evidencias viajan por **HTTPS** hacia los servicios de aplicación.  
MQTT se utiliza principalmente para **eventos y comandos IoT**, por ejemplo detección física y órdenes `OPEN` / `CLOSE`.

---

## Flujo de funcionamiento

El flujo implementado en SmartPark es el siguiente:

1. **Espera de vehículo.**
2. El sensor **HC-SR04** mide continuamente la distancia.
3. Cuando se detecta presencia, el ESP32 genera un evento `VEHICLE_DETECTED`.
4. El evento se publica mediante MQTT en AWS IoT Core.
5. El Edge activa el procesamiento visual.
6. Se detecta y realiza tracking del vehículo.
7. Se determina el tipo de movimiento: entrada o salida.
8. Se captura el rostro.
9. Se captura la placa.
10. Las evidencias son enviadas al procesamiento de IA/OCR.
11. El backend consulta usuario, vehículo y permisos.
12. Se obtiene una decisión:
    - `AUTHORIZED`
    - `DENIED`
13. El evento queda registrado en la base de datos.
14. Si corresponde, se publica un comando para la barrera.
15. El ESP32 recibe `OPEN` o `CLOSE` y acciona el servo SG90.

---

## Tecnologías principales

| Área | Tecnologías |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| IA facial | RetinaFace, ArcFace |
| Detección / tracking | YOLO11n, ByteTrack |
| OCR / placas | servicio OCR + detector de placa |
| Edge | Python, OpenCV |
| IoT | ESP32, HC-SR04, SG90 |
| Mensajería | MQTT sobre TLS |
| Base de datos | PostgreSQL |
| Cloud | AWS |
| Contenedores | Docker |
| Registro de imágenes | Amazon ECR |
| Evidencias | Amazon S3 |
| Hosting web | AWS Amplify |
| API pública | Amazon API Gateway |

---

## Estructura del repositorio

```text
Proyecto/
├── ai/                       # Servicio de inteligencia artificial
├── backend/                  # API principal y lógica de negocio
├── docs/                     # Documentación técnica del proyecto
├── edge/                     # Procesamiento local de la garita
├── firmware/
│   └── esp32/                # Firmware del ESP32
├── frontend/                 # Aplicación web React + Vite
├── infra/                    # Recursos y configuración de infraestructura
├── models/                   # Modelos necesarios por los servicios
├── mosquitto/                # Configuración MQTT local/de pruebas
├── ocr/                      # Servicio OCR de matrículas
├── smartpark_edge_installer/ # Instalador/launcher del Edge
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── package.json
├── package-lock.json
├── probar_camaras.py
└── README.md
```

> Los archivos `.env`, certificados privados, claves, embeddings biométricos, entornos virtuales, `node_modules`, builds y artefactos generados deben permanecer fuera del repositorio mediante `.gitignore`.

---

# Componentes del sistema

## Edge Computing

El Edge ejecuta la lógica que necesita respuesta inmediata junto a la garita.

Funciones principales:

- adquisición de video;
- detección del vehículo;
- tracking;
- selección de frames;
- detección de rostro;
- captura de placa;
- comunicación con AWS;
- exposición de video y estados en tiempo real.

El sistema puede trabajar con CPU o GPU NVIDIA cuando CUDA está disponible.

### API local del Edge

Por defecto:

```text
http://127.0.0.1:9000
```

Rutas utilizadas durante las pruebas:

```text
GET  /health
GET  /status
GET  /video
POST /demo/trigger
```

---

## IoT y MQTT

El hardware IoT está compuesto por:

- **ESP32**: microcontrolador con conectividad Wi-Fi;
- **HC-SR04**: sensor ultrasónico para detectar presencia;
- **SG90**: microservo utilizado como actuador de la barrera.

### Topics MQTT

Detección de vehículo:

```text
smartpark/gates/gate-01/detection
```

Ejemplo de payload:

```json
{
  "device_id": "gate-01",
  "event": "VEHICLE_DETECTED",
  "distance_cm": 3.70
}
```

Comandos de barrera:

```text
smartpark/gates/gate-01/command
```

Mensajes:

```text
OPEN
CLOSE
```

La comunicación con AWS IoT Core se realiza mediante MQTT/TLS.

---

## Inteligencia artificial y visión artificial

SmartPark utiliza diferentes modelos de visión artificial según la etapa del flujo.

### Procesamiento Edge

- **YOLO11n** para detección;
- **ByteTrack** para seguimiento;
- OpenCV para procesamiento de frames;
- captura del mejor frame para reducir información innecesaria enviada a la nube.

### Reconocimiento facial

El servicio de IA utiliza:

- **RetinaFace** para detección de rostro;
- **ArcFace** para generación y comparación de embeddings faciales.

El reconocimiento compara la representación biométrica obtenida de la imagen con los perfiles registrados.

### Placas

La lectura de matrícula se ejecuta mediante un servicio OCR dedicado. Durante las pruebas se reconoció la placa utilizada en el prototipo y se retornaron valores de confianza junto con el texto detectado.

---

## Backend

El backend está desarrollado con **FastAPI** y concentra la lógica principal del sistema.

Responsabilidades:

- usuarios;
- vehículos;
- permisos;
- autenticación;
- personal;
- eventos de acceso;
- perfiles faciales;
- autorización;
- auditoría de barrera;
- conexión a RDS;
- comunicación con IA;
- almacenamiento de evidencia;
- integración IoT.

Puerto local:

```text
8000
```

Documentación Swagger local:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend

La interfaz web está desarrollada con **React + Vite**.

Incluye dos vistas principales:

### Administración

- Dashboard
- Usuarios
- Vehículos
- Permisos
- Historial
- Auditoría de barrera
- Prueba de acceso
- Guardias y personal

### Guardia

- estado del Edge;
- estado del backend;
- sensor;
- video de la garita;
- etapas del flujo automático;
- último resultado AWS;
- eventos recientes;
- control manual de barrera.

---

# Infraestructura AWS

La solución utiliza varios servicios de AWS.

## AWS Amplify

Hospeda el frontend web de producción.

```text
https://production.d1kzks9pms1av2.amplifyapp.com
```

## API Gateway

Proporciona una entrada HTTPS pública hacia el backend.

```text
https://2uz85rgfg7.execute-api.us-east-1.amazonaws.com
```

Health check:

```text
https://2uz85rgfg7.execute-api.us-east-1.amazonaws.com/health
```

## EC2 + Auto Scaling

Se utilizan grupos de Auto Scaling separados para:

- Backend
- Inteligencia artificial

El diseño permite aumentar la cantidad de instancias sin modificar la aplicación.

Configuración observada en el proyecto:

- Backend: instancias de clase `t3.micro`;
- IA: instancias de clase `t3.large`;
- capacidad configurada dentro de un rango aproximado de 2 a 3 instancias por grupo.

## Elastic Load Balancing

Se utilizan Application Load Balancers para distribuir tráfico entre instancias.

- Backend ALB: público;
- IA ALB: interno.

## Amazon ECR

Repositorios privados:

```text
smartpark-backend
smartpark-ai
smartpark-ocr
```

Las imágenes Docker se publican en ECR y posteriormente son consumidas por las instancias desplegadas.

## Amazon RDS

Base de datos PostgreSQL administrada por AWS.

Contiene, entre otras entidades:

- usuarios;
- vehículos;
- permisos;
- eventos de acceso;
- perfiles faciales;
- muestras;
- personal;
- acciones de barrera.

## Amazon S3

Se utiliza almacenamiento de objetos para evidencias y contenido asociado.

Ejemplos de buckets utilizados en el proyecto:

```text
smartpark-uce-media-...
smartpark-uce-frontend-...
```

La estructura de evidencias permite organizar archivos por usuario y tipo de contenido.

## AWS IoT Core

Gestiona la comunicación MQTT entre el dispositivo físico y AWS.

Objeto IoT principal:

```text
gate-01
```

También se utilizaron objetos relacionados con la cámara/garita durante las pruebas.

---

## Base de datos

SmartPark utiliza PostgreSQL.

En desarrollo puede ejecutarse mediante Docker.  
En producción se utiliza **Amazon RDS PostgreSQL**.

El backend utiliza SQLAlchemy/Psycopg para la conexión.

La variable de conexión se configura mediante:

```text
DATABASE_URL
```

---

## Almacenamiento de evidencias

Las evidencias visuales se almacenan fuera de la base de datos. La base conserva referencias y metadatos, mientras que los archivos se almacenan en S3.

Ejemplo conceptual:

```text
users/
└── <user_id>/
    └── face/
        ├── image_1.jpg
        ├── image_2.jpg
        └── image_3.jpg
```

Esto evita almacenar imágenes pesadas directamente dentro de PostgreSQL.

---

# Endpoints y servicios

## Backend público AWS

Base:

```text
https://2uz85rgfg7.execute-api.us-east-1.amazonaws.com
```

Ejemplos:

```text
GET  /health
GET  /api/v1/users
GET  /api/v1/vehicles
GET  /api/v1/permissions
GET  /api/v1/access-events
POST /api/v1/access/process
POST /api/v1/access/authorize
```

Existen además rutas para autenticación, personal, perfiles faciales y barrera.

## IA local

```text
http://127.0.0.1:8001/docs
```

Rutas verificadas durante el desarrollo:

```text
GET  /health
GET  /ready
POST /face/enroll
POST /face
POST /face-legacy
POST /vehicle
POST /vehicle-track
POST /process
```

## OCR local

```text
http://127.0.0.1:8002/docs
```

Rutas principales:

```text
GET  /health
POST /plate
```

---

# Ejecución local

## Requisitos

- Git
- Docker Desktop
- Python 3.11+
- Node.js / npm
- cámara local o DroidCam
- opcional: GPU NVIDIA con CUDA
- para IoT físico: ESP32 + HC-SR04 + SG90

## 1. Clonar el repositorio

```bash
git clone https://github.com/kevinSixx/SmartPark.git
cd SmartPark/Proyecto
```

## 2. Configurar variables

Crear el archivo local desde el ejemplo:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Completar únicamente los valores correspondientes al entorno local.

> Nunca subir `.env`, claves privadas, certificados o secretos al repositorio.

## 3. Docker Compose

Validar configuración:

```bash
docker compose config
```

Levantar servicios definidos en Compose:

```bash
docker compose up -d --build
```

Ver contenedores:

```bash
docker ps
```

Ver logs:

```bash
docker compose logs -f
```

Detener:

```bash
docker compose down
```

## 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

## 5. Edge

El proyecto incluye los scripts del Edge y un instalador/launcher dentro de:

```text
edge/
smartpark_edge_installer/
```

Antes de iniciar debe verificarse:

- cámara disponible;
- URL del backend;
- URL del servicio OCR;
- modo CPU/GPU;
- configuración de `gate-01`.

---

# Despliegue

El flujo general de despliegue utilizado es:

```text
Código fuente
   |
   v
Docker build
   |
   v
Amazon ECR
   |
   v
AMI / Launch Template
   |
   v
Auto Scaling Group
   |
   v
Application Load Balancer
   |
   v
API Gateway
```

Para el frontend:

```text
React + Vite
   |
   v
AWS Amplify
   |
   v
URL pública HTTPS
```

---

# Seguridad

Este repositorio **no debe contener credenciales reales**.

No deben versionarse:

```text
.env
*.pem
*.key
certificados privados
credenciales AWS
AUTH_SECRET_KEY
embeddings biométricos
fotografías privadas
tokens
secrets.h
```

El archivo:

```text
.env.example
```

debe contener únicamente nombres de variables y valores de ejemplo que no sean secretos.

Antes de publicar una nueva versión se recomienda ejecutar:

```bash
git status
git ls-files
```

y revisar el historial para comprobar que no existan secretos versionados.

---

# Pruebas realizadas

Durante el desarrollo se verificaron, entre otras, las siguientes funciones:

- health checks de Backend, IA y OCR;
- conexión Backend ↔ PostgreSQL;
- consulta de usuarios;
- consulta de vehículos;
- consulta de permisos;
- reconocimiento facial;
- detección y lectura de placa;
- procesamiento combinado rostro + placa;
- autorización de acceso;
- registro de eventos;
- visualización del historial;
- ejecución del Edge;
- video en tiempo real;
- detección y tracking;
- captura de rostro;
- captura de placa;
- MQTT desde ESP32 hacia AWS IoT Core;
- recepción de evento `VEHICLE_DETECTED`;
- publicación de comandos `OPEN` y `CLOSE`;
- actuación del servo SG90;
- operación de la interfaz administrativa;
- operación de la interfaz del guardia;
- despliegue del frontend con Amplify;
- Auto Scaling y balanceo de carga;
- imágenes Docker en ECR;
- almacenamiento de evidencias en S3.

---

# Resultado del prototipo

El prototipo permite demostrar un flujo completo:

```text
Vehículo
   ↓
HC-SR04
   ↓
ESP32
   ↓
AWS IoT Core
   ↓
Edge / Cámara
   ↓
Detección + Tracking
   ↓
Rostro + Placa
   ↓
IA + OCR
   ↓
Backend
   ↓
RDS / Permisos
   ↓
AUTHORIZED / DENIED
   ↓
Registro del evento
   ↓
Comando IoT
   ↓
Barrera
```

---

# Limitaciones y mejoras futuras

El proyecto es un prototipo académico y puede seguir mejorándose.

Posibles mejoras:

- instalación definitiva de cámaras IP;
- procesamiento Edge en hardware dedicado;
- integración de una barrera industrial;
- alta disponibilidad multi-AZ más completa;
- dominio personalizado y certificados administrados;
- CI/CD automatizado;
- monitoreo con CloudWatch;
- gestión de secretos con AWS Secrets Manager;
- pruebas automatizadas;
- métricas de precisión de IA;
- cifrado y políticas de retención de evidencias;
- administración de múltiples garitas;
- notificaciones en tiempo real;
- dashboards analíticos;
- control de roles y permisos más granular.

---

# URLs principales

| Servicio | URL |
|---|---|
| Frontend de producción | `https://production.d1kzks9pms1av2.amplifyapp.com` |
| API Gateway | `https://2uz85rgfg7.execute-api.us-east-1.amazonaws.com` |
| Health Backend AWS | `https://2uz85rgfg7.execute-api.us-east-1.amazonaws.com/health` |
| Backend local Swagger | `http://127.0.0.1:8000/docs` |
| IA local Swagger | `http://127.0.0.1:8001/docs` |
| OCR local Swagger | `http://127.0.0.1:8002/docs` |
| Edge local | `http://127.0.0.1:9000` |

---

# Repositorio

Repositorio principal:

```text
https://github.com/kevinSixx/SmartPark
```

La implementación principal se encuentra en:

```text
Proyecto/
```

---

## Nota académica

SmartPark UCE fue desarrollado como proyecto integrador con fines académicos, demostrando la integración de conocimientos de:

- computación en la nube;
- Internet de las Cosas;
- inteligencia artificial;
- desarrollo web;
- bases de datos;
- redes y APIs;
- arquitectura de software.

---

**SmartPark UCE — Universidad Central del Ecuador**
