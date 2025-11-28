; Script para Inno Setup - Instalador Simulador Evolutivo

[Setup]
AppName=Simulador Evolutivo - AST
AppVersion=1.0.0
AppPublisher=Sistema de Resistencia Bacteriana
AppPublisherURL=https://github.com/JhoneiroLove/simulator_resistance
AppSupportURL=https://github.com/JhoneiroLove/simulator_resistance/issues
AppUpdatesURL=https://github.com/JhoneiroLove/simulator_resistance/releases
DefaultDirName={autopf}\SimuladorEvolutivo
DefaultGroupName=Simulador Evolutivo
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=Output
OutputBaseFilename=SimuladorEvolutivo_v1.0.0_Setup
Compression=lzma2/max
SolidCompression=yes
SetupIconFile=simulador_evolutivo.ico
UninstallDisplayIcon={app}\simulador_evolutivo.ico
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; GroupDescription: "Accesos directos"; Flags: unchecked

[Files]
; Copiar ejecutable y todo el contenido de la carpeta dist (simulador.exe y libs)
Source: "dist\SimuladorEvolutivo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Copiar icono para acceso directo
Source: "simulador_evolutivo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Acceso directo en menú inicio
Name: "{group}\Simulador Evolutivo"; Filename: "{app}\SimuladorEvolutivo.exe"; IconFilename: "{app}\simulador_evolutivo.ico"

; Acceso directo en escritorio (opcional, según tarea)
Name: "{commondesktop}\Simulador Evolutivo"; Filename: "{app}\SimuladorEvolutivo.exe"; IconFilename: "{app}\simulador_evolutivo.ico"; Tasks: desktopicon

[Run]
; Ejecutar app al finalizar la instalación
Filename: "{app}\SimuladorEvolutivo.exe"; Description: "Ejecutar Simulador Evolutivo"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Borrar carpeta de instalación completa al desinstalar
Type: filesandordirs; Name: "{app}"