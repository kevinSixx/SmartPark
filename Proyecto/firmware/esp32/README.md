# Firmware ESP32 de SmartPark UCE

`entradav2 (1).ino` es una copia exacta del firmware usado físicamente; el original permanece en `Proyecto/`. Conecta un ESP32, sensor ultrasónico **HC-SR04** y servo **SG90** a AWS IoT Core mediante Wi-Fi y MQTT con TLS.

## Conexiones y contrato

Según el sketch: TRIG GPIO **5**, ECHO GPIO **18**, servo GPIO **19**. La detección se publica en `smartpark/gates/gate-01/detection` con `{"device_id":"gate-01","event":"VEHICLE_DETECTED","distance_cm":15.32}`; recibe `OPEN`/`CLOSE` en `smartpark/gates/gate-01/command`. Los ángulos de cierre/apertura son los originales del sketch. Verificar el nivel lógico del pin ECHO para ESP32 y alimentar el SG90 de forma apropiada antes de probar hardware.

## Bibliotecas y secretos

El código incluye `WiFi.h`, `WiFiClientSecure.h`, `PubSubClient.h` y `ESP32Servo.h`. Crear **solo localmente** `firmware/esp32/secrets.h` a partir de `secrets.example.h` y completar `WIFI_SSID`, `WIFI_PASSWORD`, `AWS_IOT_ENDPOINT`, `AWS_CERT_CA`, `AWS_CERT_CRT` y `AWS_CERT_PRIVATE`. Los tres certificados/clave deben proporcionarse en el formato de cadenas C que requiere el sketch, sin subir el archivo real. `secrets.h` está ignorado.

## Compilar, cargar y probar después

Abrir `entradav2 (1).ino` con Arduino IDE, seleccionar la placa ESP32 y puerto correctos, y compilar con las bibliotecas ya instaladas en ese equipo. Tras revisar cables, alimentación, certificados y un entorno IoT autorizado, cargar por USB y observar el monitor serie. Para la prueba de integración, verificar publicación `VEHICLE_DETECTED` y recepción `OPEN`/`CLOSE` solo con una barrera de laboratorio. En esta organización no se compiló ni cargó el firmware y no se publicaron mensajes IoT.
