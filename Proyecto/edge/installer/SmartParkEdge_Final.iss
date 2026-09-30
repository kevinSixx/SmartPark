#define MyAppName "SmartPark UCE Edge"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Universidad Central del Ecuador"
#define MyAppExeName "SmartParkEdge.exe"
#define MyAppSourceDir "dist\SmartParkEdge"

[Setup]
AppId={{D8B85228-0FD7-4AC3-9C98-AB2F219D7F0F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SmartPark UCE Edge
DefaultGroupName=SmartPark UCE Edge
DisableProgramGroupPage=yes
OutputDir=installer\output
OutputBaseFilename=SmartParkEdgeSetup
WizardStyle=modern
Compression=lzma2/fast
SolidCompression=yes
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
; Copia TODO el paquete ONEDIR generado por PyInstaller.
; Esto incluye SmartParkEdge.exe, _internal, PyTorch, OpenCV,
; Ultralytics, AWS IoT SDK, modelos y recursos.
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\SmartPark UCE Edge"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\SmartPark UCE Edge"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar SmartPark UCE Edge"; Flags: nowait postinstall skipifsilent
