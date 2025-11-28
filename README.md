# SRB (Simulador de Resistencia Bacteriana)

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/JhoneiroLove/simulator_resistance)

---

SRB es una aplicación científica de escritorio desarrollada en Python con PyQt5 que permite simular la evolución de la resistencia bacteriana bajo distintos tratamientos. El objetivo es proporcionar una herramienta interactiva para la investigación, docencia y análisis de estrategias antimicrobianas.

## Tabla de Contenidos
- [Características](#características)
- [Capturas de Pantalla](#capturas-de-pantalla)
- [Instalación](#instalación)
- [Uso](#uso)
- [Dependencias](#dependencias)
- [Compilación y Distribución](#compilación-y-distribución)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Características
- Simulación visual e interactiva de poblaciones bacterianas.
- Modelado de tratamientos antimicrobianos y evolución de resistencia.
- Visualización de resultados detallados y mapas de calor.
- Exportación de datos y resultados.
- Interfaz moderna y personalizable.

## Capturas de Pantalla
*En proceso*

## Instalación
Para evitar conflictos y mantener las dependencias del proyecto aisladas, se recomienda encarecidamente utilizar un entorno virtual.

1.  Clona este repositorio:
    ```bash
    git clone https://github.com/JhoneiroLove/simulator_resistance.git
    cd simulator_resistance
    ```
2.  Crea y activa un entorno virtual:
    ```bash
    # Crea el entorno virtual (puedes llamarlo 'venv' o como prefieras)
    python -m venv venv

    # Activa el entorno en Windows
    .\venv\Scripts\activate
    
    # En Linux o macOS, el comando es: source venv/bin/activate
    ```
    *Una vez activado, verás `(venv)` al principio de la línea de comandos.*

3.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecuta la aplicación:
    ```bash
    python main.py
    ```

## Uso
- Al iniciar la aplicación, configura los parámetros de simulación y selecciona el tratamiento a analizar.
- Visualiza los resultados en tiempo real y explora los diferentes módulos disponibles.
- Para más detalles, consulta la documentación integrada.

## Dependencias

### Principales

- **Python**: 3.8 o superior
- **PyQt5** >=5.15.10 - Framework de interfaz gráfica
- **NumPy** >=1.24.0 - Cálculos numéricos y vectorización
- **pandas** >=2.0.0 - Análisis y manipulación de datos
- **matplotlib** >=3.7.0 - Visualización de gráficos
- **SQLAlchemy** >=2.0.0 - ORM y gestión de base de datos
- **scipy** >=1.10.0 - Algoritmos científicos
- **PyQtGraph** >=0.13.3 - Gráficos en tiempo real
- **seaborn** >=0.12.0 - Visualizaciones estadísticas

### Dependencias de Build

- **PyInstaller** >=6.3.0 - Empaquetado de ejecutables
- **Inno Setup** 6.x - Creación de instaladores (solo Windows)

Ver `requirements.txt` para la lista completa con versiones exactas.

## Compilación y Distribución

### Método Rápido (Windows)

```bash
# 1. Instala dependencias
pip install -r requirements.txt

# 2. Genera el ejecutable
./build_simulador.bat
```

El ejecutable estará en `dist/SimuladorEvolutivo/SimuladorEvolutivo.exe`

### Crear Instalador Windows

**Prerequisito:** [Inno Setup 6.x](https://jrsoftware.org/isinfo.php)

1. Genera el ejecutable primero (paso anterior)
2. Abre `setup.iss` con Inno Setup Compiler
3. `Build > Compile` (o `Ctrl+F9`)
4. El instalador se creará en `Output/SimuladorEvolutivo_v1.0.0_Setup.exe`

### Build Manual (Todas las plataformas)

```bash
# Usando la configuración personalizada
pyinstaller --clean --noconfirm simulador.spec

# O build básico desde cero
pyinstaller --clean --onedir --windowed --icon=simulador_evolutivo.ico main.py
```

### Estructura del Build

```text
SimuladorEvolutivo/
├── simulador.spec          # Configuración PyInstaller optimizada
├── build_simulador.bat     # Script automatizado (Windows)
├── setup.iss               # Script Inno Setup (instalador)
├── version_info.txt        # Metadatos del ejecutable
├── requirements.txt        # Dependencias Python
└── dist/                   # Salida del build
    └── SimuladorEvolutivo/
        ├── SimuladorEvolutivo.exe
        ├── _internal/      # Librerías y recursos
        └── data/           # Base de datos SQLite
```

### Configuración Avanzada

**simulador.spec** incluye:

- `optimize=2`: Bytecode Python optimizado
- `upx=True`: Compresión binaria
- `hiddenimports`: Módulos detectados automáticamente (PyQt5, NumPy, SciPy, etc.)
- `excludes`: Librerías no usadas eliminadas (tkinter, test, unittest)

**build_simulador.bat** verifica:

1. ✓ Python instalado y versión
2. ✓ PyInstaller disponible
3. ✓ Limpieza de builds previos
4. ✓ Compilación exitosa
5. ✓ Validación del ejecutable generado

**setup.iss** configura:

- Compresión LZMA2/max (~40% reducción)
- Wizard moderno con splash screen
- Registro de desinstalación
- Asociaciones de archivos opcionales

### Troubleshooting

#### Error: `PyInstaller no encontrado`

```bash
pip install pyinstaller>=6.3.0
```

#### Error: `Módulo no encontrado` al ejecutar .exe

Agrega el módulo a `hiddenimports` en `simulador.spec`:

```python
hiddenimports=[
    'tu_modulo_faltante',
    # ...
]
```

#### Ejecutable muy grande (>200MB)

- **Normal**: NumPy, SciPy y Matplotlib ocupan ~100-150MB
- **Reducir**: Comenta librerías no usadas en `requirements.txt` y reconstruye

#### Error al crear instalador

- Verifica que `dist/SimuladorEvolutivo/SimuladorEvolutivo.exe` exista
- Asegúrate de tener Inno Setup instalado
- Comprueba que las rutas en `setup.iss` sean correctas

#### Aplicación lenta en primera ejecución

- **Causa**: Inicialización de NumPy/SciPy y creación de base de datos
- **Solución**: Implementado lazy loading y connection pooling (optimización verde)

### Build Multiplataforma

**Linux/macOS:**

```bash
# Mismo proceso, el script .spec es portable
pyinstaller --clean --noconfirm simulador.spec

# El ejecutable estará en dist/SimuladorEvolutivo/
```

**Nota:** En Linux/macOS no se genera instalador automáticamente. Distribuye la carpeta `dist/SimuladorEvolutivo/` completa o crea un AppImage/DMG manualmente.

## Contribuir

¡Las contribuciones son bienvenidas! Por favor, abre un Issue o Pull Request para sugerir mejoras, reportar errores o proponer nuevas funcionalidades.

1. Haz un fork del proyecto.
2. Crea una rama para tu feature/fix: `git checkout -b mi-feature`
3. Haz tus cambios y realiza commits descriptivos.
4. Envía un Pull Request.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Contacto

- Autor: JhoneiroLove / DinoBudino
- Email: [jhoneiro12@hotmail.com]
- [DeepWiki](https://deepwiki.com/JhoneiroLove/simulator_resistance)

---

> SRB: Simulando el futuro de la resistencia bacteriana.
