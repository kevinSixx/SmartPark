# ============================================================
# SMARTPARK UCE
# ESP32 + SG90 SIMULADOS
#
# Este programa reemplaza temporalmente:
# - ESP32 físico
# - Servomotor SG90 físico
#
# Escucha comandos MQTT:
#
# smartpark/gates/gate-01/command
#
# {"command":"OPEN"}
# {"command":"CLOSE"}
# ============================================================

import json
import time

import paho.mqtt.client as mqtt


# ============================================================
# CONFIGURACION MQTT
# ============================================================

MQTT_HOST = "localhost"
MQTT_PORT = 1883

COMMAND_TOPIC = (
    "smartpark/gates/gate-01/command"
)

STATUS_TOPIC = (
    "smartpark/gates/gate-01/status"
)


# ============================================================
# ESTADO SIMULADO DEL SG90
# ============================================================

BARRIER_CLOSED = "CLOSED"
BARRIER_OPEN = "OPEN"

barrier_state = BARRIER_CLOSED


# Angulos simulados del servo.
SERVO_CLOSED_ANGLE = 0
SERVO_OPEN_ANGLE = 90

servo_angle = SERVO_CLOSED_ANGLE


# ============================================================
# MOSTRAR BARRERA
# ============================================================

def show_barrier():

    print()
    print(
        "========================================"
    )

    print(
        " SMARTPARK UCE - BARRERA SIMULADA"
    )

    print(
        "========================================"
    )

    print(
        f"Estado SG90 : {barrier_state}"
    )

    print(
        f"Angulo      : {servo_angle} grados"
    )

    print()


    if barrier_state == BARRIER_OPEN:

        print(
            "          |"
        )

        print(
            "          |"
        )

        print(
            "          |"
        )

        print(
            "       [ESP32]"
        )

        print()
        print(
            "BARRERA ABIERTA"
        )

    else:

        print()
        print(
            "[ESP32]=========================="
        )

        print()
        print(
            "BARRERA CERRADA"
        )


    print(
        "========================================"
    )

    print()


# ============================================================
# PUBLICAR ESTADO
# ============================================================

def publish_status(client):

    payload = {
        "device_id": "gate-01",

        "barrier": barrier_state,

        "servo_angle": servo_angle,

        "timestamp": int(
            time.time()
        )
    }


    client.publish(
        STATUS_TOPIC,
        json.dumps(payload)
    )


    print(
        f"[MQTT] Estado publicado: "
        f"{payload}"
    )


# ============================================================
# ABRIR BARRERA
# ============================================================

def open_barrier(client):

    global barrier_state
    global servo_angle


    if barrier_state == BARRIER_OPEN:

        print(
            "[SG90 SIMULADO] "
            "La barrera ya esta abierta."
        )

        return


    print()
    print(
        "[ESP32 SIMULADO] "
        "Ejecutando comando OPEN..."
    )


    # Simulamos movimiento del servo.
    for angle in range(
        SERVO_CLOSED_ANGLE,
        SERVO_OPEN_ANGLE + 1,
        15
    ):

        servo_angle = angle

        print(
            f"[SG90 SIMULADO] "
            f"Angulo: {servo_angle} grados"
        )

        time.sleep(0.08)


    servo_angle = (
        SERVO_OPEN_ANGLE
    )

    barrier_state = (
        BARRIER_OPEN
    )


    print()
    print(
        "[SG90 SIMULADO] "
        "Barrera ABIERTA."
    )


    show_barrier()

    publish_status(
        client
    )


# ============================================================
# CERRAR BARRERA
# ============================================================

def close_barrier(client):

    global barrier_state
    global servo_angle


    if barrier_state == BARRIER_CLOSED:

        print(
            "[SG90 SIMULADO] "
            "La barrera ya esta cerrada."
        )

        return


    print()
    print(
        "[ESP32 SIMULADO] "
        "Ejecutando comando CLOSE..."
    )


    # Simulamos movimiento de regreso.
    for angle in range(
        SERVO_OPEN_ANGLE,
        SERVO_CLOSED_ANGLE - 1,
        -15
    ):

        servo_angle = angle

        print(
            f"[SG90 SIMULADO] "
            f"Angulo: {servo_angle} grados"
        )

        time.sleep(0.08)


    servo_angle = (
        SERVO_CLOSED_ANGLE
    )

    barrier_state = (
        BARRIER_CLOSED
    )


    print()
    print(
        "[SG90 SIMULADO] "
        "Barrera CERRADA."
    )


    show_barrier()

    publish_status(
        client
    )


# ============================================================
# MQTT CONECTADO
# ============================================================

def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties=None
):

    print()
    print(
        "[MQTT] ESP32 simulado conectado."
    )

    print(
        f"[MQTT] Broker: "
        f"{MQTT_HOST}:{MQTT_PORT}"
    )

    print(
        f"[MQTT] Escuchando:"
    )

    print(
        f"       {COMMAND_TOPIC}"
    )

    print()


    client.subscribe(
        COMMAND_TOPIC
    )


    publish_status(
        client
    )


# ============================================================
# MQTT MENSAJE RECIBIDO
# ============================================================

def on_message(
    client,
    userdata,
    message
):

    raw_message = (
        message.payload
        .decode("utf-8")
    )


    print()
    print(
        "----------------------------------------"
    )

    print(
        f"[MQTT] Mensaje recibido:"
    )

    print(
        raw_message
    )

    print(
        "----------------------------------------"
    )


    try:

        data = json.loads(
            raw_message
        )


    except json.JSONDecodeError:

        print(
            "[ESP32 SIMULADO] "
            "JSON invalido."
        )

        return


    command = (
        str(
            data.get(
                "command",
                ""
            )
        )
        .upper()
        .strip()
    )


    if command == "OPEN":

        open_barrier(
            client
        )


    elif command == "CLOSE":

        close_barrier(
            client
        )


    else:

        print(
            f"[ESP32 SIMULADO] "
            f"Comando desconocido: "
            f"{command}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "========================================"
    )

    print(
        " SMARTPARK UCE"
    )

    print(
        " ESP32 + SG90 SIMULADOS"
    )

    print(
        "========================================"
    )

    print()


    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )


    client.on_connect = (
        on_connect
    )

    client.on_message = (
        on_message
    )


    try:

        print(
            "[MQTT] Conectando con Mosquitto..."
        )


        client.connect(
            MQTT_HOST,
            MQTT_PORT,
            60
        )


        show_barrier()


        print(
            "[ESP32 SIMULADO] "
            "Esperando comandos..."
        )

        print(
            "[ESP32 SIMULADO] "
            "Ctrl+C para salir."
        )

        print()


        client.loop_forever()


    except KeyboardInterrupt:

        print()
        print(
            "[ESP32 SIMULADO] "
            "Sistema detenido."
        )


    except Exception as error:

        print()
        print(
            "[ERROR]"
        )

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )


    finally:

        try:
            client.disconnect()

        except Exception:
            pass


if __name__ == "__main__":

    main()