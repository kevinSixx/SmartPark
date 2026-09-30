SMARTPARK EDGE V2 - CORRECCIONES
================================

Esta versión corrige DOS cosas:

1. TECLA S
-----------
Ahora la tecla S se presiona con la ventana de video SmartPark activa,
igual que la tecla Q.

NO es necesario seleccionar la terminal.

El HC-SR04 REAL sigue funcionando simultáneamente por AWS IoT.

2. TORCHVISION NMS
------------------
El primer EXE mostró:

    operator torchvision::nms does not exist

El código Python normal funciona, por lo que el problema era el empaquetado.

SmartParkEdge_v2.spec incluye explícitamente:

    torch
    torchvision
    torchvision._C
    torchvision.ops
    DLL/PYD de torch/torchvision

COMPILAR
--------
Copia en smartpark_edge_installer:

    smartpark_launcher_release_v2.py
    SmartParkEdge_v2.spec
    build_smartpark_exe_v2.ps1

Luego, con el .venv que YA funciona:

    powershell -ExecutionPolicy Bypass -File .\build_smartpark_exe_v2.ps1

PROBAR
------
Ejecuta:

    dist\SmartParkEdge\SmartParkEdge.exe

La carpeta _internal ES PARTE DEL PROGRAMA.
No la borres.

Todavía NO es un instalador de Windows.
Es una aplicación portable ONEDIR.

El instalador con interfaz "Siguiente > Instalar" se genera después
con Inno Setup y copiará toda esa carpeta automáticamente.
