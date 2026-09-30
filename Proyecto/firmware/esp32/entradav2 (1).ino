#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

#include "secrets.h"


// ============================================================
// SMARTPARK UCE
// GATE-01
// ESP32 + HC-SR04 + SG90 + AWS IoT Core
// ============================================================


// ============================================================
// PINS
// ============================================================

#define TRIG_PIN 5
#define ECHO_PIN 18
#define SERVO_PIN 19


// ============================================================
// IDENTIDAD DEL DISPOSITIVO
// ============================================================

#define DEVICE_ID "gate-01"
#define MQTT_CLIENT_ID "gate-01"


// ============================================================
// MQTT TOPICS
// ============================================================

// ESP32 -> AWS
#define AWS_IOT_PUBLISH_TOPIC \
  "smartpark/gates/gate-01/detection"

// AWS -> ESP32
#define AWS_IOT_COMMAND_TOPIC \
  "smartpark/gates/gate-01/command"


// ============================================================
// MQTT CLIENT
// ============================================================

WiFiClientSecure secureClient;
PubSubClient mqttClient(secureClient);


// ============================================================
// SERVO SG90
// ============================================================

Servo barrierServo;

#define BARRIER_CLOSED 0
#define BARRIER_OPEN 90


// ============================================================
// HC-SR04
// ============================================================

// Distancia en centímetros a partir de la cual
// consideramos que existe un vehículo.
//
// Después podemos calibrar este valor físicamente.
const float VEHICLE_DISTANCE = 20.0;

bool vehiclePresent = false;


// ============================================================
// LEER DISTANCIA HC-SR04
// ============================================================

float getDistance() {

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);


  long duration = pulseIn(
    ECHO_PIN,
    HIGH,
    30000
  );


  // No hubo respuesta del sensor
  if (duration == 0) {

    return -1;
  }


  // Velocidad aproximada del sonido:
  // 0.0343 cm/us
  //
  // Se divide para 2 porque la señal
  // va y regresa.
  float distance =
    duration * 0.0343 / 2.0;


  return distance;
}


// ============================================================
// ABRIR BARRERA
// ============================================================

void openBarrier() {

  Serial.println();
  Serial.println("==========================");
  Serial.println("[BARRIER] OPEN");
  Serial.println("==========================");

  barrierServo.write(
    BARRIER_OPEN
  );
}


// ============================================================
// CERRAR BARRERA
// ============================================================

void closeBarrier() {

  Serial.println();
  Serial.println("==========================");
  Serial.println("[BARRIER] CLOSED");
  Serial.println("==========================");

  barrierServo.write(
    BARRIER_CLOSED
  );
}


// ============================================================
// MENSAJES RECIBIDOS DESDE AWS
// ============================================================

void messageReceived(
  char* topic,
  byte* payload,
  unsigned int length
) {

  String message = "";


  for (
    unsigned int i = 0;
    i < length;
    i++
  ) {

    message += (char)payload[i];
  }


  // Elimina espacios o saltos de línea
  message.trim();


  Serial.println();
  Serial.println("--------------------------------");

  Serial.print("[MQTT] Topic recibido: ");
  Serial.println(topic);

  Serial.print("[MQTT] Comando: ");
  Serial.println(message);

  Serial.println("--------------------------------");


  // ========================================================
  // OPEN
  // ========================================================

  if (message == "OPEN") {

    openBarrier();
  }


  // ========================================================
  // CLOSE
  // ========================================================

  else if (message == "CLOSE") {

    closeBarrier();
  }


  // ========================================================
  // COMANDO DESCONOCIDO
  // ========================================================

  else {

    Serial.print(
      "[MQTT] Comando desconocido: "
    );

    Serial.println(message);
  }
}


// ============================================================
// CONECTAR WIFI
// ============================================================

void connectWiFi() {

  Serial.println();
  Serial.println("==========================");
  Serial.println("[WIFI] Conectando...");
  Serial.println("==========================");


  WiFi.mode(
    WIFI_STA
  );


  WiFi.begin(
    WIFI_SSID,
    WIFI_PASSWORD
  );


  while (
    WiFi.status() != WL_CONNECTED
  ) {

    delay(500);

    Serial.print(".");
  }


  Serial.println();

  Serial.println(
    "[WIFI] Conectado correctamente."
  );


  Serial.print(
    "[WIFI] IP local: "
  );

  Serial.println(
    WiFi.localIP()
  );
}


// ============================================================
// CONFIGURAR Y CONECTAR AWS IOT CORE
// ============================================================

void connectAWS() {

  // --------------------------------------------------------
  // Certificado raíz de Amazon
  // --------------------------------------------------------

  secureClient.setCACert(
    AWS_CERT_CA
  );


  // --------------------------------------------------------
  // Certificado del ESP32
  // --------------------------------------------------------

  secureClient.setCertificate(
    AWS_CERT_CRT
  );


  // --------------------------------------------------------
  // Clave privada del ESP32
  // --------------------------------------------------------

  secureClient.setPrivateKey(
    AWS_CERT_PRIVATE
  );


  // --------------------------------------------------------
  // Endpoint AWS IoT
  // Puerto MQTT TLS = 8883
  // --------------------------------------------------------

  mqttClient.setServer(
    AWS_IOT_ENDPOINT,
    8883
  );


  // --------------------------------------------------------
  // Callback para recibir comandos
  // --------------------------------------------------------

  mqttClient.setCallback(
    messageReceived
  );


  // --------------------------------------------------------
  // Intentar conexión
  // --------------------------------------------------------

  while (
    !mqttClient.connected()
  ) {

    Serial.println();

    Serial.print(
      "[AWS IoT] Conectando como "
    );

    Serial.println(
      MQTT_CLIENT_ID
    );


    if (
      mqttClient.connect(
        MQTT_CLIENT_ID
      )
    ) {

      Serial.println(
        "[AWS IoT] CONECTADO."
      );


      // Suscribirse al topic de comandos
      bool subscribed =
        mqttClient.subscribe(
          AWS_IOT_COMMAND_TOPIC
        );


      if (subscribed) {

        Serial.print(
          "[MQTT] Suscrito a: "
        );

        Serial.println(
          AWS_IOT_COMMAND_TOPIC
        );

      } else {

        Serial.println(
          "[MQTT] Error al suscribirse."
        );
      }

    } else {

      Serial.print(
        "[AWS IoT] Error. Estado MQTT: "
      );

      Serial.println(
        mqttClient.state()
      );


      Serial.println(
        "[AWS IoT] Reintentando en 2 segundos..."
      );


      delay(2000);
    }
  }
}


// ============================================================
// ENVIAR EVENTO VEHICLE_DETECTED A AWS
// ============================================================

void sendVehicleEvent(
  float distance
) {

  // JSON esperado por SmartPark:
  //
  // {
  //   "device_id": "gate-01",
  //   "event": "VEHICLE_DETECTED",
  //   "distance_cm": 15.32
  // }


  String payload = "{";


  payload +=
    "\"device_id\":\"";

  payload +=
    DEVICE_ID;

  payload +=
    "\",";


  payload +=
    "\"event\":\"VEHICLE_DETECTED\",";


  payload +=
    "\"distance_cm\":";

  payload +=
    String(
      distance,
      2
    );


  payload += "}";


  Serial.println();
  Serial.println("--------------------------------");

  Serial.print(
    "[MQTT] Publicando en: "
  );

  Serial.println(
    AWS_IOT_PUBLISH_TOPIC
  );


  Serial.print(
    "[MQTT] Payload: "
  );

  Serial.println(
    payload
  );


  bool success =
    mqttClient.publish(
      AWS_IOT_PUBLISH_TOPIC,
      payload.c_str()
    );


  if (success) {

    Serial.println(
      "[MQTT] Evento enviado correctamente."
    );

  } else {

    Serial.println(
      "[MQTT] ERROR enviando evento."
    );
  }


  Serial.println("--------------------------------");
}


// ============================================================
// SETUP
// ============================================================

void setup() {

  Serial.begin(
    115200
  );


  delay(1000);


  Serial.println();
  Serial.println();
  Serial.println("================================");
  Serial.println("       SMARTPARK UCE");
  Serial.println("       GATE-01");
  Serial.println("================================");


  // ========================================================
  // HC-SR04
  // ========================================================

  pinMode(
    TRIG_PIN,
    OUTPUT
  );


  pinMode(
    ECHO_PIN,
    INPUT
  );


  digitalWrite(
    TRIG_PIN,
    LOW
  );


  // ========================================================
  // SG90
  // ========================================================

  barrierServo.setPeriodHertz(
    50
  );


  barrierServo.attach(
    SERVO_PIN,
    500,
    2400
  );


  // Iniciar con barrera cerrada
  closeBarrier();


  // ========================================================
  // WIFI
  // ========================================================

  connectWiFi();


  // ========================================================
  // AWS IOT CORE
  // ========================================================

  connectAWS();


  Serial.println();
  Serial.println("================================");
  Serial.println(" SMARTPARK GATE-01 READY");
  Serial.println("================================");

  Serial.println();

  Serial.print(
    "[MQTT] Detection topic: "
  );

  Serial.println(
    AWS_IOT_PUBLISH_TOPIC
  );


  Serial.print(
    "[MQTT] Command topic: "
  );

  Serial.println(
    AWS_IOT_COMMAND_TOPIC
  );

  Serial.println();
}


// ============================================================
// LOOP
// ============================================================

void loop() {

  // ========================================================
  // RECONEXIÓN WIFI
  // ========================================================

  if (
    WiFi.status() != WL_CONNECTED
  ) {

    Serial.println(
      "[WIFI] Conexion perdida."
    );

    connectWiFi();
  }


  // ========================================================
  // RECONEXIÓN AWS IOT
  // ========================================================

  if (
    !mqttClient.connected()
  ) {

    Serial.println(
      "[AWS IoT] Conexion perdida."
    );

    connectAWS();
  }


  // Mantiene MQTT funcionando
  mqttClient.loop();


  // ========================================================
  // LEER SENSOR HC-SR04
  // ========================================================

  float distance =
    getDistance();


  if (
    distance > 0
  ) {

    Serial.print(
      "[HC-SR04] Distance: "
    );

    Serial.print(
      distance
    );

    Serial.println(
      " cm"
    );


    // ======================================================
    // VEHÍCULO LLEGA
    // ======================================================

    if (
      distance < VEHICLE_DISTANCE &&
      !vehiclePresent
    ) {

      vehiclePresent = true;


      Serial.println();
      Serial.println("==========================");
      Serial.println("VEHICLE DETECTED");
      Serial.println("==========================");


      // Enviar evento a AWS IoT Core
      sendVehicleEvent(
        distance
      );
    }


    // ======================================================
    // VEHÍCULO SE RETIRA
    // ======================================================

    if (
      distance >= VEHICLE_DISTANCE &&
      vehiclePresent
    ) {

      vehiclePresent = false;


      Serial.println();
      Serial.println(
        "[HC-SR04] Vehicle left."
      );
    }
  }


  delay(
    250
  );
}