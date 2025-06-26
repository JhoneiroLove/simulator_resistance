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
- Para más detalles, consulta la documentación integrada o el menú de ayuda.

## Dependencias
- Python 3.8+
- PyQt5
- numpy
- pandas
- matplotlib
- (Ver `requirements.txt` para la lista completa)

## Compilación y Distribución
El proceso para generar el ejecutable y el instalador se divide en dos pasos manuales para asegurar la máxima compatibilidad.

### Paso 1: Generar el ejecutable con PyInstaller

1.  **Asegúrate de tener un entorno virtual activado** con todas las dependencias del proyecto instaladas (ver sección de [Instalación](#instalación)).
2.  Ejecuta el script de compilación:
    ```bash
    build_simulador.bat
    ```
3.  Este script utilizará **PyInstaller** para empaquetar la aplicación. Al finalizar, encontrarás todos los archivos del programa en la carpeta `dist\SimuladorEvolutivo`.

### Paso 2: Crear el instalador con Inno Setup

Una vez que los archivos del programa han sido creados en la carpeta `dist/`, puedes empaquetarlos en un instalador.

1.  **Requisito:** Debes tener [Inno Setup](https://jrsoftware.org/isinfo.php) instalado en tu sistema.
2.  Abre la aplicación **Inno Setup Compiler**.
3.  Ve a `File > Open` y selecciona el archivo `setup.iss` que se encuentra en la raíz del proyecto.
4.  Una vez abierto el script, ve al menú `Build > Compile` (o presiona `Ctrl+F9`).
5.  Inno Setup tomará los archivos de la carpeta `dist\SimuladorEvolutivo`, los comprimirá y generará el instalador final (`SimuladorEvolutivo_Instalador.exe`) en una nueva carpeta llamada `Output`.

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