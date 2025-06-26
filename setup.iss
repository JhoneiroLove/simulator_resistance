; Script para Inno Setup - Instalador Simulador Evolutivo

[Setup]
; Información básica
AppName=Simulador Evolutivo
AppVersion=1.0
DefaultDirName={pf}\SimuladorEvolutivo
DefaultGroupName=Simulador Evolutivo
OutputBaseFilename=SimuladorEvolutivo_Instalador
Compression=lzma
SolidCompression=yes

; Icono del instalador
SetupIconFile=simulador_evolutivo.ico

; Permitir elevación de privilegios para crear accesos y escribir en Archivos de Programa
PrivilegesRequired=admin

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