@echo off
REM ================================
REM Build automatizado para el Simulador Evolutivo
REM ================================

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Limpiar builds previos (carpetas dist y build)
echo Limpiando builds anteriores...
rmdir /S /Q dist
rmdir /S /Q build

REM Ejecutar PyInstaller con el spec
echo Iniciando construcción del ejecutable...
pyinstaller simulador.spec

REM Revisar si la construcción fue exitosa
if exist dist\SimuladorEvolutivo\SimuladorEvolutivo.exe (
    echo =================================================
    echo ¡EXE creado con éxito!
    echo Archivo generado: dist\SimuladorEvolutivo\SimuladorEvolutivo.exe
    echo =================================================
) else (
    echo =================================================
    echo ERROR: No se pudo generar el ejecutable.
    echo Revisa los logs de PyInstaller arriba.
    echo =================================================
)

pause
