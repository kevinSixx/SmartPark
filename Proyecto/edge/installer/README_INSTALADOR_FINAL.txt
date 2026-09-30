SMARTPARK UCE EDGE - INSTALADOR FINAL
====================================

REQUISITO PREVIO
----------------
La versión portable V2 ya debe funcionar:

    dist\SmartParkEdge\SmartParkEdge.exe

CREAR EL INSTALADOR
-------------------
1. Copia en la raíz de smartpark_edge_installer:

    SmartParkEdge_Final.iss
    crear_instalador_final.ps1

2. Ejecuta:

    powershell -ExecutionPolicy Bypass -File .\crear_instalador_final.ps1

3. Si Inno Setup 6 no está instalado, el script preguntará si quieres
   instalarlo usando winget.

4. Al terminar tendrás:

    installer\output\SmartParkEdgeSetup.exe

QUÉ HACE SmartParkEdgeSetup.exe
-------------------------------
El usuario verá un instalador normal de Windows:

    Bienvenido
    -> carpeta de instalación
    -> Instalar
    -> barra de progreso
    -> Finalizar

El instalador copia el paquete generado por PyInstaller a:

    C:\Program Files\SmartPark UCE Edge\

Incluye dentro del programa:

    - Python runtime
    - PyTorch
    - Torchvision
    - CUDA runtime empaquetado
    - OpenCV
    - Ultralytics
    - AWS IoT SDK
    - FastAPI/Uvicorn
    - YOLO11n
    - YuNet
    - detector YOLO de matrículas
    - ByteTrack
    - recursos SmartPark

La otra PC NO necesita instalar Python, pip, VS Code ni el .venv.

AL ABRIR SMARTPARK
------------------
Aparece la configuración de:

    - Gate ID
    - cámara
    - AUTO / CPU / GPU

Después inicia el sistema.

Se mantienen:

    - HC-SR04 REAL por AWS IoT
    - tecla S sobre la ventana de video para simular el sensor
    - tecla Q para salir

IMPORTANTE - GPU
----------------
Para usar GPU NVIDIA, la otra PC debe tener una GPU compatible y un
driver NVIDIA adecuado.

Si CUDA no está disponible:

    AUTO -> CPU

IMPORTANTE - IOT
----------------
El instalador de laboratorio actual contiene las credenciales IoT de
gate-01 porque forman parte del paquete probado.

NO distribuyas públicamente este instalador con esa private key.

Para varias garitas, cada instalación debe tener credenciales IoT
propias.
