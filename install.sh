#!/bin/bash
# Script de instalación multiplataforma para Simulador Evolutivo
# RNF-2: Instalación
# Soporta: Linux, macOS

set -e

echo "==================================="
echo "Simulador Evolutivo AST - Instalador"
echo "==================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    echo "Por favor instala Python 3.8 o superior desde https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
echo "✓ Python detectado: $PYTHON_VERSION"

# Verificar versión mínima (3.8)
if [ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]; then
    echo "ERROR: Se requiere Python 3.8 o superior (detectado: $PYTHON_VERSION)"
    exit 1
fi

# Crear entorno virtual
echo ""
echo "Creando entorno virtual..."
if [ -d "venv" ]; then
    echo "⚠ Entorno virtual ya existe, se recreará"
    rm -rf venv
fi

python3 -m venv venv
echo "✓ Entorno virtual creado"

# Activar entorno virtual
echo ""
echo "Activando entorno virtual..."
source venv/bin/activate
echo "✓ Entorno activado"

# Actualizar pip
echo ""
echo "Actualizando pip..."
pip install --upgrade pip --quiet
echo "✓ pip actualizado"

# Instalar dependencias
echo ""
echo "Instalando dependencias..."
pip install -r requirements.txt --quiet
echo "✓ Dependencias instaladas"

# Inicializar base de datos
echo ""
echo "Inicializando base de datos..."
if [ -f "scripts/init_database.py" ]; then
    python scripts/init_database.py
    echo "✓ Base de datos inicializada"
else
    echo "⚠ Script de inicialización no encontrado, se creará al primer uso"
fi

# Verificar instalación
echo ""
echo "Verificando instalación..."
python -c "from PyQt5.QtWidgets import QApplication; import numpy; import sqlalchemy; print('✓ Imports principales correctos')"

echo ""
echo "==================================="
echo "✓ Instalación completada exitosamente"
echo "==================================="
echo ""
echo "Para ejecutar la aplicación:"
echo "  1. Activa el entorno: source venv/bin/activate"
echo "  2. Ejecuta: python main.py"
echo ""
