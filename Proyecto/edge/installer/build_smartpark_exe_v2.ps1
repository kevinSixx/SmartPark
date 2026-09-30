$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================"
Write-Host " SMARTPARK UCE EDGE - BUILD V2"
Write-Host " Sensor real + S en video + torchvision completo"
Write-Host "============================================================"
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$required = @(
    "smartpark_launcher_release_v2.py",
    "smartpark_edge.py",
    "smartpark_gate_cloud.py",
    "SmartParkEdge_v2.spec",
    "yolo11n.pt",
    "ai\bytetrack_smartpark.yaml",
    "models\smartpark\face_detection_yunet_2023mar.onnx",
    "models\smartpark\license_plate_yolov8n.pt",
    "certs\camera\AmazonRootCA1.pem",
    "certs\camera\camera-certificate.pem.crt",
    "certs\camera\camera-private.pem.key"
)

foreach ($item in $required) {
    if (-not (Test-Path $item)) {
        throw "Falta archivo requerido: $item"
    }
}

Write-Host "[1/3] Python y versiones..."
python --version

Write-Host ""
python -c "import torch, torchvision; print('Torch:', torch.__version__); print('Torchvision:', torchvision.__version__); print('CUDA:', torch.version.cuda); print('CUDA disponible:', torch.cuda.is_available())"

Write-Host ""
Write-Host "[2/3] PyInstaller..."
python -m pip install --upgrade pyinstaller

if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
}

if (Test-Path "dist") {
    Remove-Item "dist" -Recurse -Force
}

Write-Host ""
Write-Host "[3/3] Construyendo EXE..."
python -m PyInstaller --clean --noconfirm SmartParkEdge_v2.spec

$exe = "dist\SmartParkEdge\SmartParkEdge.exe"

if (-not (Test-Path $exe)) {
    throw "No se creo $exe"
}

Write-Host ""
Write-Host "============================================================"
Write-Host " EXE V2 CREADO"
Write-Host "============================================================"
Write-Host ""
Write-Host "Ejecuta:"
Write-Host "  $exe"
Write-Host ""
Write-Host "Prueba:"
Write-Host "  - AWS IoT conectado"
Write-Host "  - HC-SR04 real sigue activo"
Write-Host "  - Click en ventana de video y presiona S"
Write-Host "  - Q cierra SmartPark"
Write-Host "  - Tracking YOLO/ByteTrack NO debe mostrar torchvision::nms"
Write-Host ""
