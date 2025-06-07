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

REM Revisar si la construcción fue exitosa y crear instalador
if exist dist\SimuladorEvolutivo\SimuladorEvolutivo.exe (
    echo =================================================
    echo ¡EXE creado con éxito!
    echo Archivo generado: dist\SimuladorEvolutivo\SimuladorEvolutivo.exe
    echo =================================================

    REM Crear instalador con Inno Setup
    REM Buscar ISCC.exe automáticamente
    where ISCC.exe >nul 2>&1
    if %ERRORLEVEL%==0 (
        for /f "delims=" %%i in ('where ISCC.exe') do set "INNOSETUP_PATH=%%i"
    ) else (
        REM Fallback: ruta típica de instalación, personalizar si es necesario
        set "INNOSETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    )

    if exist "%DIST_DIR%\%EXE_NAME%" (
        echo =================================================
        echo ¡EXE creado con éxito!
        echo Archivo generado: %DIST_DIR%\%EXE_NAME%
        echo =================================================

        if exist "%INNOSETUP_PATH%" (
            echo Iniciando creación del instalador con Inno Setup...
            "%INNOSETUP_PATH%" setup.iss
            if exist %INSTALLER_NAME% (
                echo =================================================
                echo ¡Instalador creado con éxito!
                echo Archivo generado: %INSTALLER_NAME%
                echo =================================================
            ) else (
                echo =================================================
                echo ERROR: No se pudo crear el instalador.
                echo Verifica el script setup.iss y la salida de Inno Setup.
                echo =================================================
            )
        ) else (
            echo =================================================
            echo ERROR: No se encontró Inno Setup (ISCC.exe) en el PATH ni en la ruta por defecto.
            echo Por favor, revisa la variable INNOSETUP_PATH en este script.
            echo =================================================
        )
    ) else (
        echo =================================================
        echo ERROR: No se pudo generar el ejecutable.
        echo Revisa los logs de PyInstaller arriba.
        echo =================================================
    )
) else (
    echo =================================================
    echo ERROR: No se pudo generar el ejecutable.
    echo Revisa los logs de PyInstaller arriba.
    echo =================================================
)

pause
