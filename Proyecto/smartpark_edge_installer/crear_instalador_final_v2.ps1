$ErrorActionPreference = "Stop"

# UTF-8 para que PowerShell muestre texto correctamente.
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

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

# ------------------------------------------------------------
# 1. Verificar portable
# ------------------------------------------------------------

if (-not (Test-Path $portableExe)) {
    Write-Host "ERROR: No encuentro:"
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

# ------------------------------------------------------------
# 2. Buscar Inno Setup de forma robusta
# ------------------------------------------------------------

function Find-InnoSetupCompiler {
    # 1) PATH
    $cmd = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($cmd -and (Test-Path $cmd.Source)) {
        return $cmd.Source
    }

    # 2) Rutas comunes (incluye instalación por usuario)
    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Inno Setup 6\ISCC.exe"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    # 3) Registro de Windows
    $registryRoots = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    )

    foreach ($rootKey in $registryRoots) {
        if (-not (Test-Path $rootKey)) {
            continue
        }

        $apps = Get-ChildItem $rootKey -ErrorAction SilentlyContinue

        foreach ($app in $apps) {
            try {
                $props = Get-ItemProperty $app.PSPath -ErrorAction Stop
                $name = [string]$props.DisplayName

                if ($name -like "Inno Setup*") {
                    $installLocation = [string]$props.InstallLocation

                    if ($installLocation) {
                        $candidate = Join-Path $installLocation "ISCC.exe"

                        if (Test-Path $candidate) {
                            return $candidate
                        }
                    }

                    $displayIcon = [string]$props.DisplayIcon

                    if ($displayIcon) {
                        $iconPath = $displayIcon.Split(",")[0].Trim('"')
                        $folder = Split-Path -Parent $iconPath

                        if ($folder) {
                            $candidate = Join-Path $folder "ISCC.exe"

                            if (Test-Path $candidate) {
                                return $candidate
                            }
                        }
                    }
                }
            } catch {}
        }
    }

    # 4) Búsqueda limitada en carpetas probables
    $searchRoots = @(
        "$env:LOCALAPPDATA\Programs",
        "${env:ProgramFiles(x86)}",
        "$env:ProgramFiles"
    )

    foreach ($searchRoot in $searchRoots) {
        if (-not $searchRoot -or -not (Test-Path $searchRoot)) {
            continue
        }

        try {
            $found = Get-ChildItem `
                -Path $searchRoot `
                -Filter "ISCC.exe" `
                -File `
                -Recurse `
                -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -match "Inno Setup" } |
                Select-Object -First 1

            if ($found) {
                return $found.FullName
            }
        } catch {}
    }

    return $null
}

$iscc = Find-InnoSetupCompiler

if ($iscc) {
    Write-Host "[2/3] Inno Setup encontrado:"
    Write-Host "  $iscc"
}
else {
    Write-Host "[2/3] Inno Setup 6 no fue localizado."
    Write-Host ""
    Write-Host "Intentaremos instalarlo con winget."
    Write-Host ""

    $winget = Get-Command "winget.exe" -ErrorAction SilentlyContinue

    if (-not $winget) {
        Write-Host "ERROR: winget no está disponible."
        Write-Host "Instala Inno Setup 6 manualmente y vuelve a ejecutar este script."
        exit 1
    }

    # IMPORTANTE:
    # winget puede devolver un código distinto de 0 cuando el paquete YA existe.
    # Por eso NO abortamos aquí: después volvemos a buscar ISCC.exe.
    winget install `
        --id JRSoftware.InnoSetup `
        -e `
        --accept-package-agreements `
        --accept-source-agreements

    Write-Host ""
    Write-Host "Volviendo a buscar Inno Setup..."
    Start-Sleep -Seconds 2

    $iscc = Find-InnoSetupCompiler

    if (-not $iscc) {
        Write-Host ""
        Write-Host "No pude localizar ISCC.exe aunque winget indica que Inno Setup puede estar instalado."
        Write-Host ""
        Write-Host "Prueba cerrar y abrir PowerShell y ejecutar este mismo script otra vez."
        Write-Host ""
        Write-Host "También puedes abrir Inno Setup desde el menú Inicio para confirmar que está instalado."
        exit 1
    }

    Write-Host "[2/3] Inno Setup localizado:"
    Write-Host "  $iscc"
}

# ------------------------------------------------------------
# 3. Compilar instalador
# ------------------------------------------------------------

Write-Host ""
Write-Host "[3/3] Creando SmartParkEdgeSetup.exe..."
Write-Host "Puede tardar porque SmartPark incluye PyTorch, CUDA y modelos."
Write-Host ""

if (Test-Path "installer\output") {
    Remove-Item "installer\output" -Recurse -Force
}

New-Item -ItemType Directory -Path "installer\output" -Force | Out-Null

& $iscc $issFile

if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup terminó con error (codigo $LASTEXITCODE)."
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
Write-Host "Este es el archivo que puedes pasar a otra PC."
Write-Host ""
