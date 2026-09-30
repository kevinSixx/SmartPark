$ErrorActionPreference = "Stop"

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

Write-Host ""
Write-Host "============================================================"
Write-Host " SMARTPARK UCE EDGE - INSTALADOR FINAL V3"
Write-Host "============================================================"
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$portableDir = Join-Path $root "dist\SmartParkEdge"
$portableExe = Join-Path $portableDir "SmartParkEdge.exe"
$outputDir = Join-Path $root "installer\output"
$outputSetup = Join-Path $outputDir "SmartParkEdgeSetup.exe"

if (-not (Test-Path $portableExe)) {
    throw "No encuentro $portableExe. Primero compila el EXE V2."
}

Write-Host "[1/4] Portable encontrado:"
Write-Host "  $portableExe"
Write-Host ""

function Find-InnoSetupCompiler {
    $cmd = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($cmd -and (Test-Path $cmd.Source)) {
        return $cmd.Source
    }

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

    $registryRoots = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    )

    foreach ($rootKey in $registryRoots) {
        if (-not (Test-Path $rootKey)) { continue }

        foreach ($app in (Get-ChildItem $rootKey -ErrorAction SilentlyContinue)) {
            try {
                $props = Get-ItemProperty $app.PSPath -ErrorAction Stop
                $name = [string]$props.DisplayName

                if ($name -like "Inno Setup*") {
                    $installLocation = [string]$props.InstallLocation

                    if ($installLocation) {
                        $candidate = Join-Path $installLocation "ISCC.exe"
                        if (Test-Path $candidate) { return $candidate }
                    }

                    $displayIcon = [string]$props.DisplayIcon
                    if ($displayIcon) {
                        $iconPath = $displayIcon.Split(",")[0].Trim('"')
                        $folder = Split-Path -Parent $iconPath

                        if ($folder) {
                            $candidate = Join-Path $folder "ISCC.exe"
                            if (Test-Path $candidate) { return $candidate }
                        }
                    }
                }
            } catch {}
        }
    }

    return $null
}

$iscc = Find-InnoSetupCompiler

if (-not $iscc) {
    throw "Inno Setup 6 parece no estar disponible. Ábrelo una vez desde Inicio y vuelve a ejecutar este script."
}

Write-Host "[2/4] Inno Setup encontrado:"
Write-Host "  $iscc"
Write-Host ""

# ============================================================
# SOLUCIÓN AL ERROR DE RUTA LARGA
# ============================================================
#
# El paquete de PyTorch contiene rutas internas muy profundas.
# El proyecto actual también está dentro de una ruta muy larga.
#
# Inno Setup terminó con:
#   "El sistema no puede encontrar la ruta especificada"
#
# después de comprimir archivos de torch.
#
# Montamos temporalmente dist\SmartParkEdge como una unidad corta:
#
#   Z:\
#
# De esta manera Inno lee:
#
#   Z:\_internal\torch...
#
# en lugar de toda la ruta larga del proyecto.
# ============================================================

$driveCandidates = @("Z:", "Y:", "X:", "W:", "V:", "U:")
$buildDrive = $null

foreach ($candidate in $driveCandidates) {
    if (-not (Test-Path "$candidate\")) {
        $buildDrive = $candidate
        break
    }
}

if (-not $buildDrive) {
    throw "No encontré una letra de unidad libre entre Z:, Y:, X:, W:, V: y U:."
}

$portableFull = (Resolve-Path $portableDir).Path

Write-Host "[3/4] Creando ruta corta temporal:"
Write-Host "  $buildDrive -> $portableFull"

# SUBST devuelve texto/código externo; comprobamos después la unidad.
& subst $buildDrive $portableFull

if (-not (Test-Path "$buildDrive\")) {
    throw "No se pudo crear la unidad temporal $buildDrive"
}

try {
    if (Test-Path $outputDir) {
        Remove-Item $outputDir -Recurse -Force
    }

    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

    # Inno acepta ruta absoluta en OutputDir.
    $outputEscaped = $outputDir

    $issTemp = Join-Path $env:TEMP "SmartParkEdge_Final_ShortPath.iss"

    $issContent = @"
#define MyAppName "SmartPark UCE Edge"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Universidad Central del Ecuador"
#define MyAppExeName "SmartParkEdge.exe"

[Setup]
AppId={{D8B85228-0FD7-4AC3-9C98-AB2F219D7F0F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SmartPark UCE Edge
DefaultGroupName=SmartPark UCE Edge
DisableProgramGroupPage=yes
OutputDir=$outputEscaped
OutputBaseFilename=SmartParkEdgeSetup
WizardStyle=modern
Compression=lzma2/fast
SolidCompression=no
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: checkedonce

[Files]
Source: "$buildDrive\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\SmartPark UCE Edge"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\SmartPark UCE Edge"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar SmartPark UCE Edge"; Flags: nowait postinstall skipifsilent
"@

    # Inno Setup maneja bien UTF-8 con BOM.
    Set-Content -Path $issTemp -Value $issContent -Encoding UTF8

    Write-Host ""
    Write-Host "[4/4] Creando SmartParkEdgeSetup.exe..."
    Write-Host "Puede tardar: PyTorch/CUDA hacen que el paquete sea grande."
    Write-Host ""

    & $iscc $issTemp

    if ($LASTEXITCODE -ne 0) {
        throw "Inno Setup terminó con error (código $LASTEXITCODE)."
    }

    if (-not (Test-Path $outputSetup)) {
        throw "Inno terminó, pero no apareció: $outputSetup"
    }

    $item = Get-Item $outputSetup
    $sizeMB = [math]::Round($item.Length / 1MB, 1)

    Write-Host ""
    Write-Host "============================================================"
    Write-Host " INSTALADOR CREADO ✅"
    Write-Host "============================================================"
    Write-Host ""
    Write-Host "Archivo:"
    Write-Host "  $outputSetup"
    Write-Host ""
    Write-Host "Tamaño:"
    Write-Host "  $sizeMB MB"
    Write-Host ""
    Write-Host "Este SmartParkEdgeSetup.exe ya es el instalador para otra PC."
    Write-Host ""
}
finally {
    Write-Host "Eliminando unidad temporal $buildDrive ..."
    & subst $buildDrive /D | Out-Null
}
