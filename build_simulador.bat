@echo off
REM ================================
REM Build Script - Simulador Evolutivo
REM ================================

setlocal enabledelayedexpansion

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

echo ========================================
echo Simulador Evolutivo - Build Process
echo ========================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instale Python 3.8 o superior.
    pause
    exit /b 1
)
echo OK - Python detectado
echo.

REM Verificar PyInstaller
echo [2/5] Verificando PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller no encontrado.
    echo Instalando PyInstaller...
    pip install pyinstaller
)
echo OK - PyInstaller disponible
echo.

REM Limpiar builds previos
echo [3/5] Limpiando builds anteriores...
if exist dist rmdir /S /Q dist
if exist build rmdir /S /Q build
echo OK - Directorio limpio
echo.

REM Ejecutar PyInstaller con el spec
echo [4/5] Construyendo ejecutable...
python -m PyInstaller --clean --noconfirm simulador.spec

echo.

REM Revisar si la construcción fue exitosa
echo [5/5] Verificando resultado...
if not exist "dist\SimuladorEvolutivo\SimuladorEvolutivo.exe" (
    echo.
    echo ========================================
    echo ERROR: Build fallido
    echo ========================================
    echo No se pudo generar el ejecutable.
    echo Revise los logs de PyInstaller arriba.
    echo ========================================
    pause
    exit /b 1
)

echo OK - Ejecutable generado
echo.
echo ========================================
echo BUILD EXITOSO
echo ========================================
echo.
echo Ubicacion: dist\SimuladorEvolutivo\
echo Ejecutable: SimuladorEvolutivo.exe
echo.
echo Siguiente paso:
echo - Probar: dist\SimuladorEvolutivo\SimuladorEvolutivo.exe
echo - Instalar: Compilar setup.iss con Inno Setup
echo ========================================
echo.
pause