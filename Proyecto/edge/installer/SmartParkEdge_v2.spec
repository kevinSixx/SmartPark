# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_all,
    collect_submodules,
    collect_data_files,
)

ROOT = Path(SPECPATH)


# ============================================================
# PYTORCH
# ============================================================
#
# SmartPark funciona correctamente dentro del .venv.
#
# En el primer EXE faltaron componentes binarios de torchvision,
# por lo que YOLO/ByteTrack terminó con:
#
#     operator torchvision::nms does not exist
#
# Se incluyen explícitamente torch y torchvision completos.
# ============================================================

torch_datas, torch_binaries, torch_hidden = collect_all(
    "torch"
)

tv_datas, tv_binaries, tv_hidden = collect_all(
    "torchvision"
)


# ============================================================
# ULTRALYTICS
# ============================================================

ultra_datas, ultra_binaries, ultra_hidden = collect_all(
    "ultralytics"
)


# ============================================================
# AWS CRT / IOT
# ============================================================

crt_datas, crt_binaries, crt_hidden = collect_all(
    "awscrt"
)


# ============================================================
# OPENCV DATA
# ============================================================

opencv_datas = collect_data_files(
    "cv2",
    includes=[
        "data/*.xml",
    ],
)


# ============================================================
# HIDDEN IMPORTS
# ============================================================

hiddenimports = []

hiddenimports += torch_hidden
hiddenimports += tv_hidden
hiddenimports += ultra_hidden
hiddenimports += crt_hidden

hiddenimports += collect_submodules(
    "awsiot"
)

hiddenimports += collect_submodules(
    "uvicorn"
)

hiddenimports += [
    "smartpark_edge",
    "smartpark_gate_cloud",

    # Importante para las operaciones C++/CUDA de torchvision.
    "torchvision._C",
    "torchvision.ops",
    "torchvision.ops.boxes",
]


# ============================================================
# DATOS SMARTPARK
# ============================================================

datas = [
    (
        str(
            ROOT
            /
            "yolo11n.pt"
        ),
        ".",
    ),

    (
        str(
            ROOT
            /
            "ai"
            /
            "bytetrack_smartpark.yaml"
        ),
        "ai",
    ),

    (
        str(
            ROOT
            /
            "models"
            /
            "smartpark"
            /
            "face_detection_yunet_2023mar.onnx"
        ),
        "models/smartpark",
    ),

    (
        str(
            ROOT
            /
            "models"
            /
            "smartpark"
            /
            "license_plate_yolov8n.pt"
        ),
        "models/smartpark",
    ),

    (
        str(
            ROOT
            /
            "certs"
            /
            "camera"
            /
            "AmazonRootCA1.pem"
        ),
        "certs/camera",
    ),

    (
        str(
            ROOT
            /
            "certs"
            /
            "camera"
            /
            "camera-certificate.pem.crt"
        ),
        "certs/camera",
    ),

    (
        str(
            ROOT
            /
            "certs"
            /
            "camera"
            /
            "camera-private.pem.key"
        ),
        "certs/camera",
    ),
]

datas += torch_datas
datas += tv_datas
datas += ultra_datas
datas += crt_datas
datas += opencv_datas


# ============================================================
# BINARIOS
# ============================================================

binaries = []

binaries += torch_binaries
binaries += tv_binaries
binaries += ultra_binaries
binaries += crt_binaries


# ============================================================
# PYINSTALLER
# ============================================================

a = Analysis(
    [
        "smartpark_launcher_release_v2.py"
    ],

    pathex=[
        str(ROOT)
    ],

    binaries=binaries,

    datas=datas,

    hiddenimports=hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[],

    noarchive=False,

    optimize=0,
)


pyz = PYZ(
    a.pure
)


exe = EXE(
    pyz,
    a.scripts,
    [],

    exclude_binaries=True,

    name="SmartParkEdge",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=False,

    # Se deja consola para ver logs de diagnóstico.
    # La tecla S YA NO depende de esta consola;
    # se detecta en la ventana OpenCV.
    console=True,

    disable_windowed_traceback=False,
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,

    strip=False,

    upx=False,

    upx_exclude=[],

    name="SmartParkEdge",
)
