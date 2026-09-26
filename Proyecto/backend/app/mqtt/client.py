import os
import time
from functools import lru_cache

import boto3


# ============================================================
# CONFIGURACION AWS IOT
# ============================================================

AWS_REGION = os.getenv(
    "AWS_REGION",
    "us-east-1"
)

AWS_IOT_ENDPOINT = os.getenv(
    "AWS_IOT_ENDPOINT",
    ""
)

AWS_IOT_COMMAND_TOPIC = os.getenv(
    "AWS_IOT_COMMAND_TOPIC",
    "smartpark/gates/gate-01/command"
)

AWS_IOT_ENABLED = (
    os.getenv(
        "AWS_IOT_ENABLED",
        "false"
    )
    .strip()
    .lower()
    in {"1", "true", "yes", "on"}
)

BARRIER_OPEN_SECONDS = int(
    os.getenv(
        "BARRIER_OPEN_SECONDS",
        "5"
    )
)


# ============================================================
# AWS IOT CLIENT
# ============================================================

@lru_cache(maxsize=1)
def get_iot_client():

    if not AWS_IOT_ENDPOINT:
        raise RuntimeError(
            "AWS_IOT_ENDPOINT no esta configurado"
        )

    endpoint_url = (
        f"https://{AWS_IOT_ENDPOINT}"
    )

    return boto3.client(
        "iot-data",
        region_name=AWS_REGION,
        endpoint_url=endpoint_url
    )


# ============================================================
# PUBLICAR COMANDO
# ============================================================

def publish_command(
    command: str
) -> bool:

    command = (
        command
        .strip()
        .upper()
    )

    if command not in {
        "OPEN",
        "CLOSE"
    }:

        raise ValueError(
            f"Comando IoT no permitido: {command}"
        )


    # Permite seguir usando el backend localmente
    # sin AWS IoT.
    if not AWS_IOT_ENABLED:

        print(
            f"[AWS IOT] Deshabilitado. "
            f"No se publica {command}."
        )

        return False


    client = get_iot_client()


    print(
        f"[AWS IOT] Publicando "
        f"{command} en "
        f"{AWS_IOT_COMMAND_TOPIC}"
    )


    client.publish(
        topic=AWS_IOT_COMMAND_TOPIC,
        qos=0,
        payload=command.encode("utf-8")
    )


    print(
        f"[AWS IOT] Comando "
        f"{command} publicado."
    )

    return True


# ============================================================
# CICLO DE BARRERA PARA DEMO
# ============================================================

def open_and_close_barrier():

    try:

        publish_command(
            "OPEN"
        )


        print(
            f"[BARRIER] Esperando "
            f"{BARRIER_OPEN_SECONDS} segundos..."
        )


        time.sleep(
            BARRIER_OPEN_SECONDS
        )


        publish_command(
            "CLOSE"
        )


    except Exception as error:

        # Importante:
        # un problema de IoT no debe tumbar FastAPI.
        print(
            f"[AWS IOT] Error controlando "
            f"la barrera: {error}"
        )