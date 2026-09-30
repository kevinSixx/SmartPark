$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================"
Write-Host " SMARTPARK UCE EDGE - CREAR INSTALADOR WINDOWS"
Write-Host "============================================================"
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$portableExe = "dist\SmartParkEdge\SmartParkEdge.exe"
$issFile = "SmartParkEdge_Final.iss"
$outputSetup = "installer\output\SmartParkEdgeSetup.exe"

if (-not (Test-Path $portableExe)) {
    Write-Host "ERROR: No encuentro el ejecutable portable:"
    Write-Host "  $portableExe"
    Write-Host ""
    Write-Host "Primero ejecuta:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\build_smartpark_exe_v2.ps1"
    exit 1
}

if (-not (Test-Path $issFile)) {
    Write-Host "ERROR: Falta:"
    Write-Host "  $issFile"
    exit 1
}

Write-Host "[1/3] SmartParkEdge.exe encontrado OK"
Write-Host ""

# Buscar Inno Setup 6.
$candidates = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)

$iscc = $null

foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path $candidate)) {
        $iscc = $candidate
        break
    }
}

if (-not $iscc) {
    $cmd = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($cmd) {
        $iscc = $cmd.Source
    }
}

if (-not $iscc) {
    Write-Host "[2/3] Inno Setup 6 no está instalado."
    Write-Host ""
    Write-Host "Para crear el instalador necesitamos instalarlo UNA sola vez."
    Write-Host ""

    $answer = Read-Host "¿Quieres instalar Inno Setup 6 ahora con winget? (S/N)"

    if ($answer.Trim().ToUpper() -ne "S") {
        Write-Host ""
        Write-Host "Instálalo manualmente y vuelve a ejecutar este script."
        exit 0
    }

    $winget = Get-Command "winget.exe" -ErrorAction SilentlyContinue

    if (-not $winget) {
        Write-Host ""
        Write-Host "No encuentro winget en este Windows."
        Write-Host "Instala Inno Setup 6 manualmente y vuelve a ejecutar este script."
        exit 1
    }

    Write-Host ""
    Write-Host "Instalando Inno Setup 6..."
    winget install --id JRSoftware.InnoSetup -e --accept-package-agreements --accept-source-agreements

    if ($LASTEXITCODE -ne 0) {
        throw "winget no pudo instalar Inno Setup."
    }

    # Buscar otra vez después de instalar.
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            $iscc = $candidate
            break
        }
    }

    if (-not $iscc) {
        Write-Host ""
        Write-Host "Inno Setup parece haberse instalado, pero esta terminal todavía no lo ve."
        Write-Host "Cierra PowerShell, abre uno nuevo y ejecuta este script otra vez."
        exit 0
    }
}
else {
    Write-Host "[2/3] Inno Setup encontrado:"
    Write-Host "  $iscc"
}

Write-Host ""
Write-Host "[3/3] Empaquetando SmartParkEdgeSetup.exe..."
Write-Host "Esto puede tardar porque SmartPark incluye PyTorch/CUDA/modelos."
Write-Host ""

if (Test-Path "installer\output") {
    Remove-Item "installer\output" -Recurse -Force
}

New-Item -ItemType Directory -Path "installer\output" -Force | Out-Null

& $iscc $issFile

if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup terminó con error."
}

if (-not (Test-Path $outputSetup)) {
    throw "La compilación terminó pero no apareció $outputSetup"
}

$item = Get-Item $outputSetup
$sizeMB = [math]::Round($item.Length / 1MB, 1)

Write-Host ""
Write-Host "============================================================"
Write-Host " INSTALADOR CREADO CORRECTAMENTE"
Write-Host "============================================================"
Write-Host ""
Write-Host "Archivo:"
Write-Host "  $outputSetup"
Write-Host ""
Write-Host "Tamaño:"
Write-Host "  $sizeMB MB"
Write-Host ""
Write-Host "Este es el archivo que puedes ejecutar en otra PC."
Write-Host ""
