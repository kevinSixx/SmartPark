#define MyAppName "SmartPark UCE Edge"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Universidad Central del Ecuador"
#define MyAppExeName "SmartParkEdge.exe"

[Setup]
AppId={{B9D2D9D7-16A7-4C6F-A848-5EE1C597C8D4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SmartPark UCE Edge
DefaultGroupName=SmartPark UCE Edge
OutputDir=installer\output
OutputBaseFilename=SmartParkEdgeSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "dist\SmartParkEdge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\SmartPark UCE Edge"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\SmartPark UCE Edge"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar SmartPark UCE Edge"; Flags: nowait postinstall skipifsilent
