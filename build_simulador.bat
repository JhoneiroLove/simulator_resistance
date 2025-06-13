@echo off
REM ================================
REM Creación del ejecutable para el Simulador Evolutivo
REM ================================

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Limpiar builds previos
echo Limpiando builds anteriores...
if exist dist rmdir /S /Q dist
if exist build rmdir /S /Q build

REM Ejecutar PyInstaller con el spec
echo Iniciando construcción del ejecutable...
python -m PyInstaller simulador.spec

REM Revisar si la construcción fue exitosa
if not exist "dist\SimuladorEvolutivo\SimuladorEvolutivo.exe" (
    echo =================================================
    echo ERROR: No se pudo generar el ejecutable con PyInstaller.
    echo Revisa los logs de PyInstaller arriba.
    echo =================================================
    goto end
)

echo =================================================
echo .exe creado exitosamente
echo Los archivos se encuentran en la carpeta 'dist\SimuladorEvolutivo'.
echo Para crear el instalador, compila 'setup.iss' con Inno Setup.
echo =================================================

:end
echo(
echo Proceso finalizado.
pause
