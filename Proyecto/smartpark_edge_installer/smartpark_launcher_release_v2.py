"""
SmartPark UCE - Launcher instalable V2 (sensor real + S en video)
================================

Colocar este archivo en la raíz de:

    smartpark_edge_installer/

junto a:

    smartpark_edge.py
    smartpark_gate_cloud.py
    yolo11n.pt
    ai/
    certs/
    models/

Este launcher NO cambia el motor SmartPark.
Solo configura:

    - Cámara
    - AUTO / CPU / GPU
    - Gate ID

y después inicia smartpark_edge.py.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import cv2


# Carpeta del ejecutable y carpeta interna de recursos.
#
# En desarrollo:
#   APP_DIR == RESOURCE_DIR == carpeta del .py
#
# Con PyInstaller ONEDIR:
#   APP_DIR      = carpeta de SmartParkEdge.exe
#   RESOURCE_DIR = carpeta interna donde PyInstaller deja modelos/DLL/datos
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
    RESOURCE_DIR = Path(
        getattr(sys, "_MEIPASS", APP_DIR)
    ).resolve()
else:
    APP_DIR = Path(__file__).resolve().parent
    RESOURCE_DIR = APP_DIR

# Todos los módulos actuales usan rutas relativas para:
#   yolo11n.pt
#   ai/
#   models/
#   certs/
# Por eso ejecutamos el motor desde la carpeta real de recursos.
os.chdir(RESOURCE_DIR)

# Configuración escribible por el usuario.
# NO la guardamos dentro de Program Files.
LOCAL_APPDATA = Path(
    os.getenv("LOCALAPPDATA", str(Path.home()))
)
CONFIG_DIR = LOCAL_APPDATA / "SmartParkUCE"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = CONFIG_DIR / "smartpark_settings.json"

MAX_CAMERA_INDEX = 6

DEFAULT_CONFIG = {
    "camera_source": 0,
    "device": "auto",
    "gate_id": "gate-01",
}


# ============================================================
# CONFIG
# ============================================================

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return dict(DEFAULT_CONFIG)

    try:
        data = json.loads(
            CONFIG_PATH.read_text(
                encoding="utf-8"
            )
        )

        result = dict(DEFAULT_CONFIG)
        result.update(data)

        return result

    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(
    camera_source: int,
    device: str,
    gate_id: str,
) -> None:
    CONFIG_PATH.write_text(
        json.dumps(
            {
                "camera_source": camera_source,
                "device": device,
                "gate_id": gate_id,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ============================================================
# CÁMARAS
# ============================================================

def _open_camera(
    index: int,
):
    """
    Usa exactamente el método que ya funciona
    en smartpark_gate_cloud.py:
        cv2.VideoCapture(index)
    """
    cap = cv2.VideoCapture(
        index
    )

    if not cap.isOpened():
        cap.release()
        return None

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280,
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720,
    )

    time.sleep(
        0.18
    )

    frame = None

    for _ in range(6):
        ok, current = cap.read()

        if (
            ok
            and
            current is not None
            and
            current.size > 0
        ):
            frame = current
            break

        time.sleep(
            0.06
        )

    if frame is None:
        cap.release()
        return None

    return cap


def scan_cameras() -> list[int]:
    found = []

    # Intentar silenciar mensajes de OpenCV
    # durante el escaneo. No es crítico si
    # una versión concreta no soporta esto.
    try:
        cv2.setLogLevel(0)
    except Exception:
        pass

    for index in range(
        MAX_CAMERA_INDEX
    ):
        cap = _open_camera(
            index
        )

        if cap is None:
            continue

        found.append(
            index
        )

        cap.release()

    return found


def preview_camera(
    index: int,
) -> None:
    cap = _open_camera(
        index
    )

    if cap is None:
        messagebox.showerror(
            "SmartPark UCE",
            (
                f"No se pudo abrir "
                f"la Cámara {index}."
            ),
        )
        return

    window_name = (
        f"SmartPark UCE - "
        f"Vista previa Camara {index}"
    )

    try:
        while True:
            ok, frame = (
                cap.read()
            )

            if (
                not ok
                or
                frame is None
            ):
                continue

            display = (
                frame.copy()
            )

            cv2.rectangle(
                display,
                (0, 0),
                (
                    display.shape[1],
                    95,
                ),
                (0, 0, 0),
                -1,
            )

            cv2.putText(
                display,
                (
                    f"SMARTPARK UCE "
                    f"- CAMARA {index}"
                ),
                (20, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.82,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                display,
                (
                    "ESC = cerrar "
                    "vista previa"
                ),
                (20, 72),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                2,
            )

            cv2.imshow(
                window_name,
                display,
            )

            key = (
                cv2.waitKey(1)
                &
                0xFF
            )

            if key == 27:
                break

    finally:
        cap.release()

        try:
            cv2.destroyWindow(
                window_name
            )
        except Exception:
            cv2.destroyAllWindows()


# ============================================================
# APP
# ============================================================

class SmartParkLauncher:
    def __init__(
        self,
        root: tk.Tk,
    ):
        self.root = root

        self.root.title(
            "SmartPark UCE Edge"
        )

        self.root.geometry(
            "560x470"
        )

        self.root.resizable(
            False,
            False,
        )

        self.config = (
            load_config()
        )

        self.camera_map = {}

        self.camera_var = (
            tk.StringVar()
        )

        self.device_var = (
            tk.StringVar(
                value=str(
                    self.config.get(
                        "device",
                        "auto",
                    )
                ).upper()
            )
        )

        self.gate_var = (
            tk.StringVar(
                value=str(
                    self.config.get(
                        "gate_id",
                        "gate-01",
                    )
                )
            )
        )

        self.status_var = (
            tk.StringVar(
                value=(
                    "Buscando cámaras..."
                )
            )
        )

        self._build_ui()

        self.root.after(
            150,
            self.refresh_cameras,
        )

    def _build_ui(
        self,
    ):
        main = ttk.Frame(
            self.root,
            padding=24,
        )

        main.pack(
            fill="both",
            expand=True,
        )

        title = ttk.Label(
            main,
            text="SMARTPARK UCE EDGE",
            font=(
                "Segoe UI",
                20,
                "bold",
            ),
        )

        title.pack(
            pady=(
                4,
                4,
            )
        )

        subtitle = ttk.Label(
            main,
            text=(
                "Configuración de la garita"
            ),
            font=(
                "Segoe UI",
                10,
            ),
        )

        subtitle.pack(
            pady=(
                0,
                24,
            )
        )

        form = ttk.Frame(
            main
        )

        form.pack(
            fill="x"
        )

        # Gate ID
        ttk.Label(
            form,
            text="Garita / Gate ID",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=8,
        )

        gate_entry = ttk.Entry(
            form,
            textvariable=self.gate_var,
            width=32,
        )

        gate_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=8,
            padx=(
                15,
                0,
            ),
        )

        # Cámara
        ttk.Label(
            form,
            text="Cámara",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8,
        )

        camera_frame = ttk.Frame(
            form
        )

        camera_frame.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=8,
            padx=(
                15,
                0,
            ),
        )

        self.camera_combo = (
            ttk.Combobox(
                camera_frame,
                textvariable=(
                    self.camera_var
                ),
                state="readonly",
                width=22,
            )
        )

        self.camera_combo.pack(
            side="left",
            fill="x",
            expand=True,
        )

        refresh_button = ttk.Button(
            camera_frame,
            text="Actualizar",
            command=(
                self.refresh_cameras
            ),
        )

        refresh_button.pack(
            side="left",
            padx=(
                8,
                0,
            ),
        )

        # Preview
        preview_button = ttk.Button(
            form,
            text="Vista previa de cámara",
            command=(
                self.preview_selected
            ),
        )

        preview_button.grid(
            row=2,
            column=1,
            sticky="ew",
            pady=(
                2,
                12,
            ),
            padx=(
                15,
                0,
            ),
        )

        # Dispositivo
        ttk.Label(
            form,
            text="Procesamiento",
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=8,
        )

        device_combo = ttk.Combobox(
            form,
            textvariable=(
                self.device_var
            ),
            values=[
                "AUTO",
                "CPU",
                "GPU",
            ],
            state="readonly",
            width=29,
        )

        device_combo.grid(
            row=3,
            column=1,
            sticky="ew",
            pady=8,
            padx=(
                15,
                0,
            ),
        )

        device_help = ttk.Label(
            form,
            text=(
                "AUTO usa GPU NVIDIA "
                "si CUDA está disponible; "
                "si no, usa CPU."
            ),
            wraplength=330,
            justify="left",
        )

        device_help.grid(
            row=4,
            column=1,
            sticky="w",
            padx=(
                15,
                0,
            ),
            pady=(
                0,
                10,
            ),
        )

        form.columnconfigure(
            1,
            weight=1,
        )

        ttk.Separator(
            main,
            orient="horizontal",
        ).pack(
            fill="x",
            pady=18,
        )

        status = ttk.Label(
            main,
            textvariable=(
                self.status_var
            ),
            anchor="center",
        )

        status.pack(
            fill="x",
            pady=(
                0,
                15,
            ),
        )

        start_button = ttk.Button(
            main,
            text="INICIAR SMARTPARK",
            command=self.start_smartpark,
        )

        start_button.pack(
            fill="x",
            ipady=9,
        )

    def refresh_cameras(
        self,
    ):
        self.status_var.set(
            "Buscando cámaras disponibles..."
        )

        self.root.update_idletasks()

        cameras = (
            scan_cameras()
        )

        self.camera_map = {
            f"Cámara {index}": index
            for index
            in cameras
        }

        names = list(
            self.camera_map.keys()
        )

        self.camera_combo[
            "values"
        ] = names

        if not names:
            self.camera_var.set(
                ""
            )

            self.status_var.set(
                "No se encontró ninguna cámara."
            )

            return

        saved = self.config.get(
            "camera_source",
            0,
        )

        saved_name = (
            f"Cámara {saved}"
        )

        if (
            saved_name
            in
            self.camera_map
        ):
            self.camera_var.set(
                saved_name
            )
        else:
            self.camera_var.set(
                names[0]
            )

        self.status_var.set(
            (
                f"{len(names)} cámara(s) "
                f"disponible(s)."
            )
        )

    def get_selected_camera(
        self,
    ) -> int | None:
        return self.camera_map.get(
            self.camera_var.get()
        )

    def preview_selected(
        self,
    ):
        index = (
            self.get_selected_camera()
        )

        if index is None:
            messagebox.showwarning(
                "SmartPark UCE",
                (
                    "Selecciona una cámara "
                    "primero."
                ),
            )
            return

        preview_camera(
            index
        )

    def start_smartpark(
        self,
    ):
        camera_index = (
            self.get_selected_camera()
        )

        if camera_index is None:
            messagebox.showerror(
                "SmartPark UCE",
                (
                    "No hay una cámara "
                    "seleccionada."
                ),
            )
            return

        gate_id = (
            self.gate_var.get()
            .strip()
        )

        if not gate_id:
            messagebox.showerror(
                "SmartPark UCE",
                (
                    "Escribe un Gate ID, "
                    "por ejemplo gate-01."
                ),
            )
            return

        selected_ui_device = (
            self.device_var.get()
            .strip()
            .upper()
        )

        device_map = {
            "AUTO": "auto",
            "CPU": "cpu",
            "GPU": "cuda",
        }

        device = device_map.get(
            selected_ui_device,
            "auto",
        )

        save_config(
            camera_index,
            device,
            gate_id,
        )

        # smartpark_edge.py leerá esto
        # ANTES de importar torch.
        os.environ[
            "SMARTPARK_DEVICE"
        ] = device

        # Evitar menú 1/2/3 del código actual.
        sys.argv = [
            sys.argv[0],
            "--no-menu",
        ]

        self.status_var.set(
            "Iniciando SmartPark..."
        )

        self.root.update_idletasks()

        # Cerramos la interfaz de configuración.
        self.root.destroy()

        # Importar solo AHORA:
        # así SMARTPARK_DEVICE ya está configurado.
        import smartpark_edge as edge

        # Cámara elegida.
        edge.gate.CAMERA_SOURCE = (
            camera_index
        )

        # Garita elegida.
        edge.gate.TOPIC_DETECTION = (
            f"smartpark/gates/"
            f"{gate_id}/detection"
        )

        # IMPORTANTE:
        # NO cambiamos MQTT_CLIENT_ID aquí.
        #
        # smartpark_gate_cloud.py ya tiene un client_id que sabemos
        # que funciona con el certificado/política IoT actual:
        #
        #     smartpark-camera-01
        #
        # Cambiarlo automáticamente a algo como
        # "smartpark-camera-gate-01" puede hacer que AWS IoT rechace
        # la conexión si la policy permite solo el client_id original.
        #
        # Para futuras garitas (gate-02, gate-03...) se provisionará
        # un client_id/certificado/policy propios y se guardarán en config.

        # En modo demo, mantener coherente
        # el topic simulado.
        if hasattr(
            edge,
            "SIMULATED_TOPIC",
        ):
            edge.SIMULATED_TOPIC = (
                f"smartpark/gates/"
                f"{gate_id}/detection"
            )

        # Health / status.
        if hasattr(
            edge,
            "edge_state",
        ):
            edge.edge_state[
                "gate_id"
            ] = gate_id

        # ====================================================
        # SENSOR REAL + TECLA S DENTRO DEL VIDEO
        # ====================================================
        #
        # NO usamos edge.main(), porque ese main crea un hilo
        # que espera la tecla S en la TERMINAL.
        #
        # En esta versión instalable:
        #
        #   - gate.main() mantiene HC-SR04 REAL + AWS IoT.
        #   - interceptamos cv2.waitKey() para que la tecla S
        #     se pulse directamente sobre la ventana de video,
        #     igual que Q.
        #   - FastAPI local sigue activo para /health /status /video.
        #
        # El flujo real y el flujo simulado terminan llamando al
        # mismo ciclo SmartPark.
        # ====================================================

        original_wait_key = cv2.waitKey

        def smartpark_video_wait_key(delay=0):
            key = original_wait_key(delay)

            normalized = key & 0xFF

            if normalized in (
                ord("s"),
                ord("S"),
            ):
                # simulate_vehicle_detected ya tiene debounce
                # y evita disparar otro ciclo si SmartPark
                # está procesando.
                try:
                    edge.simulate_vehicle_detected()
                except Exception as exc:
                    print(
                        "[SIMULACION] Error: "
                        f"{exc}"
                    )

                # Devolvemos -1 para que el core no interprete
                # la S como ningún otro comando.
                return -1

            return key

        # cv2 es el mismo módulo compartido por launcher,
        # smartpark_edge y smartpark_gate_cloud.
        cv2.waitKey = smartpark_video_wait_key

        # API local de Edge.
        api_thread = threading.Thread(
            target=edge.run_api_server,
            daemon=True,
        )
        api_thread.start()

        time.sleep(1.0)

        print()
        print("=" * 72)
        print("SMARTPARK UCE EDGE")
        print("SENSOR REAL + SIMULACION EN VIDEO")
        print("=" * 72)
        print(
            "HC-SR04 REAL : ACTIVO mediante AWS IoT"
        )
        print(
            "Tecla S      : simular sensor DESDE la ventana de video"
        )
        print(
            "Tecla Q      : salir"
        )
        print("=" * 72)
        print()

        # Motor físico REAL.
        edge.gate.main()


def main():
    root = tk.Tk()

    # Tema nativo de Windows cuando esté disponible.
    try:
        style = ttk.Style()

        if "vista" in style.theme_names():
            style.theme_use(
                "vista"
            )

    except Exception:
        pass

    SmartParkLauncher(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()
