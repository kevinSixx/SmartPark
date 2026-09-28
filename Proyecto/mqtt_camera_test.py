import json
import time

from awscrt import mqtt
from awsiot import mqtt_connection_builder


# ============================================================
# SMARTPARK UCE
# PRUEBA PC -> AWS IOT
# ============================================================

AWS_IOT_ENDPOINT = (
    "a3e93abira4kkd-ats.iot.us-east-1.amazonaws.com"
)

CLIENT_ID = "smartpark-camera-01"

TOPIC_DETECTION = (
    "smartpark/gates/gate-01/detection"
)

ROOT_CA = "certs/camera/AmazonRootCA1.pem"

CERTIFICATE = (
    "certs/camera/camera-certificate.pem.crt"
)

PRIVATE_KEY = (
    "certs/camera/camera-private.pem.key"
)


# ============================================================
# MENSAJE RECIBIDO
# ============================================================

def on_message_received(
    topic,
    payload,
    dup,
    qos,
    retain,
    **kwargs
):

    print()
    print("=" * 60)
    print("[AWS IOT] MENSAJE RECIBIDO")
    print(f"[AWS IOT] Topic: {topic}")

    try:

        message = json.loads(
            payload.decode("utf-8")
        )

        print("[AWS IOT] Payload:")
        print(
            json.dumps(
                message,
                indent=2
            )
        )

        event = message.get(
            "event"
        )

        distance = message.get(
            "distance_cm"
        )

        if event == "VEHICLE_DETECTED":

            print()
            print("🚗 VEHICULO DETECTADO")
            print(
                f"Distancia: {distance} cm"
            )

            print()
            print(
                "AQUI SE ACTIVARA "
                "DROIDCAM."
            )

    except Exception as error:

        print(
            "[AWS IOT] Error leyendo "
            f"mensaje: {error}"
        )

    print("=" * 60)


# ============================================================
# CONEXIÓN
# ============================================================

print()
print("=" * 60)
print("SMARTPARK CAMERA MQTT TEST")
print("=" * 60)

print()
print(
    f"[AWS IOT] Endpoint: "
    f"{AWS_IOT_ENDPOINT}"
)

print(
    f"[AWS IOT] Client ID: "
    f"{CLIENT_ID}"
)

print()
print("[AWS IOT] Conectando...")


mqtt_connection = (
    mqtt_connection_builder.mtls_from_path(

        endpoint=AWS_IOT_ENDPOINT,

        cert_filepath=CERTIFICATE,

        pri_key_filepath=PRIVATE_KEY,

        ca_filepath=ROOT_CA,

        client_id=CLIENT_ID,

        clean_session=False,

        keep_alive_secs=30
    )
)


connect_future = (
    mqtt_connection.connect()
)

connect_future.result()


print("[AWS IOT] CONECTADO ✅")


# ============================================================
# SUSCRIPCIÓN
# ============================================================

print()
print(
    f"[AWS IOT] Suscribiendo a:"
)

print(
    f"          {TOPIC_DETECTION}"
)


subscribe_future, packet_id = (
    mqtt_connection.subscribe(

        topic=TOPIC_DETECTION,

        qos=mqtt.QoS.AT_LEAST_ONCE,

        callback=on_message_received
    )
)


subscribe_result = (
    subscribe_future.result()
)


print(
    "[AWS IOT] SUSCRIPCIÓN ACTIVA ✅"
)

print()
print(
    "Esperando VEHICLE_DETECTED..."
)

print(
    "Acerca algo al HC-SR04."
)

print(
    "CTRL+C para salir."
)


# ============================================================
# ESPERAR
# ============================================================

try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print()
    print(
        "[AWS IOT] Cerrando conexión..."
    )

    disconnect_future = (
        mqtt_connection.disconnect()
    )

    disconnect_future.result()

    print(
        "[AWS IOT] Desconectado."
    )