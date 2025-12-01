@echo off
REM Script de instalación para Windows
REM RNF-2: Instalación
REM Autor: Sistema AST Simulator

echo ===================================
echo Simulador Evolutivo AST - Instalador
echo ===================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python 3.8 o superior desde https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ^>^ Python detectado: %PYTHON_VERSION%

REM Crear entorno virtual
echo.
echo Creando entorno virtual...
if exist venv (
    echo ^! Entorno virtual ya existe, se recreara
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo ^>^ Entorno virtual creado

REM Activar entorno virtual
echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo ^>^ Entorno activado

REM Actualizar pip
echo.
echo Actualizando pip...
python -m pip install --upgrade pip --quiet
echo ^>^ pip actualizado

REM Instalar dependencias
echo.
echo Instalando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias
    pause
    exit /b 1
)
echo ^>^ Dependencias instaladas

REM Inicializar base de datos
echo.
echo Inicializando base de datos...
if exist scripts\init_database.py (
    python scripts\init_database.py
    echo ^>^ Base de datos inicializada
) else (
    echo ^! Script de inicializacion no encontrado, se creara al primer uso
)

REM Verificar instalación
echo.
echo Verificando instalacion...
python -c "from PyQt5.QtWidgets import QApplication; import numpy; import sqlalchemy; print('^>^ Imports principales correctos')"
if errorlevel 1 (
    echo ERROR: Fallo la verificacion
    pause
    exit /b 1
)

echo.
echo ===================================
echo ^>^ Instalacion completada exitosamente
echo ===================================
echo.
echo Para ejecutar la aplicacion:
echo   1. Activa el entorno: venv\Scripts\activate.bat
echo   2. Ejecuta: python main.py
echo.
pause
