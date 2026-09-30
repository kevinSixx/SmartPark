# Arquitectura SmartPark UCE

```mermaid
flowchart LR
  ESP32[ESP32 · HC-SR04/SG90] -->|MQTT/TLS detección| IOT[AWS IoT Core]
  IOT -->|topic detection| EDGE[Edge Windows · cámara]
  EDGE -->|POST multipart| APIGW[API Gateway]
  WEB[Frontend Amplify] --> APIGW
  WEB -->|localhost :9000| EDGE
  APIGW --> BALB[ALB Backend · ASG]
  BALB --> BACK[Backend FastAPI]
  BACK --> RDS[(RDS PostgreSQL)]
  BACK --> S3[(S3)]
  BACK -->|HTTP interno| AIALB[ALB interno IA · ASG]
  AIALB --> AI[AI FastAPI]
  AI --> OCR[OCR PaddleOCR]
  AI -->|match/authorize| BACK
  BACK -->|comando OPEN/CLOSE| IOT
  IOT --> ESP32
```

El diagrama refleja la arquitectura informada, no una comprobación de recursos AWS en esta fase. ECR almacena las imágenes Backend/AI/OCR y no aparece en la ruta de una solicitud. En local, Compose conecta DB/Backend/AI/OCR por DNS interno; Edge y firmware requieren entorno/certificados propios. Detalle verificable de red y CORS: [auditoría](../audit/12_CORS_Y_RED.md).

