# Requerimientos No Funcionales (RNF)

## RNF-01: Usabilidad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-01 |
| Nombre del Requerimiento | Interfaz Intuitiva y Usable |
| Características | Workflow guiado paso a paso, validación en tiempo real, tooltips descriptivos, feedback visual inmediato |
| Descripción del requerimiento | La interfaz debe ser intuitiva y fácil de usar mediante un workflow guiado que conduzca al usuario secuencialmente a través de las etapas de la simulación, proporcionando validación en tiempo real con mensajes de error claros, tooltips descriptivos en todos los controles y feedback visual inmediato de las acciones del usuario |
| Requerimiento Funcional relacionado | RF-19 (Workflow Guiado), RF-10 (Visualización Microplaca), RF-11 (Visualización Curvas) |
| Prioridad del requerimiento | Alta |
| Implementación | `src/gui/workflows/ast_workflow.py`, tooltips en todos los widgets, mensajes de validación en formularios |
| Validación | Flujo completo AST ejecutable sin consultar documentación |

## RNF-02: Instalación

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-02 |
| Nombre del Requerimiento | Setup Automático Multiplataforma |
| Características | Scripts de instalación automatizados, verificación de dependencias, inicialización de BD automática, creación de directorios |
| Descripción del requerimiento | El sistema debe proporcionar scripts de instalación automatizados para Windows (install.bat) y Linux/macOS (install.sh) que verifiquen la versión de Python (>=3.8), creen entorno virtual automáticamente, instalen dependencias desde requirements.txt, inicialicen la base de datos con migraciones y creen directorios necesarios (logs, data) |
| Requerimiento Funcional relacionado | RF-16 (Persistencia Datos), RF-20 (Carga Datos Científicos) |
| Prioridad del requerimiento | Alta |
| Implementación | `install.sh`, `install.bat`, `scripts/init_database.py`, `src/migrations/` |
| Validación | Instalación completa ejecutable con un solo comando, sin intervención manual |

## RNF-03: Seguridad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-03 |
| Nombre del Requerimiento | Validación y Sanitización de Entradas |
| Características | InputValidator centralizado, sanitización SQL, validación de rangos, validación de rutas, escape HTML |
| Descripción del requerimiento | El sistema debe validar y sanitizar todas las entradas de usuario mediante un InputValidator centralizado que prevenga inyección SQL usando placeholders, valide rangos numéricos (temperatura 33-37°C, inóculo 5×10⁵-5×10⁶ CFU/mL), verifique rutas de archivo contra path traversal, escape caracteres especiales HTML y registre intentos de validación fallidos |
| Requerimiento Funcional relacionado | RF-15 (Validación Entrada), RF-13 (Exportación) |
| Prioridad del requerimiento | Alta |
| Implementación | `src/utils/security.py` (InputValidator, SecurityLogger), sanitización en todos los formularios |
| Validación | 40 tests passing en `tests/test_security.py` cubriendo SQL injection, path traversal, XSS |

## RNF-04: Protección

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-04 |
| Nombre del Requerimiento | Manejo Robusto de Errores |
| Características | ErrorHandler centralizado, logging dual, rollback automático BD, decorador safe_method, recuperación de fallos |
| Descripción del requerimiento | El sistema debe manejar errores de forma robusta mediante ErrorHandler centralizado que registre eventos en logs duales (logs/app.log para INFO, logs/errors.log para ERROR), ejecute rollback automático en transacciones fallidas de base de datos, proporcione decorador @safe_method para métodos críticos con valores de fallback y permita recuperación de fallos sin pérdida de datos |
| Requerimiento Funcional relacionado | RF-17 (Manejo Errores), RF-16 (Persistencia) |
| Prioridad del requerimiento | Alta |
| Implementación | `src/utils/error_handler.py` (ErrorHandler, DatabaseErrorHandler, ThreadErrorHandler), aplicado en main.py y widgets críticos |
| Validación | Logs creados automáticamente, rollback verificado en tests de BD, aplicación no crashea ante errores |

## RNF-05: Sostenibilidad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-05 |
| Nombre del Requerimiento | Optimización de Recursos (Green Software) |
| Características | LRU cache, connection pooling, índices BD, vectorización NumPy, batch operations, lazy loading |
| Descripción del requerimiento | El sistema debe optimizar el uso de recursos computacionales mediante LRU cache para cálculos MIC (95% hit rate, 120× speedup), connection pooling SQLAlchemy (pool_size=5, max_overflow=10), índices automáticos en columnas frecuentemente consultadas, vectorización NumPy en curvas de crecimiento (10× speedup), operaciones batch para reducir I/O y lazy loading de datos bajo demanda |
| Requerimiento Funcional relacionado | RF-04 (Simulación Crecimiento), RF-05 (Cálculo MIC), RF-16 (Persistencia) |
| Prioridad del requerimiento | Alta |
| Implementación | `src/utils/green_optimization.py` (ResourceOptimizer, MemoryOptimizer, QueryOptimizer), caché en GenotypePhenotypeCalculator, vectorización en growth_models.py |
| Validación | Panel 96 wells < 10s (5.1s medido), memoria pico < 100 MB (45.2 MB medido), throughput MIC 100k ops/s |

## RNF-06: Accesibilidad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-06 |
| Nombre del Requerimiento | Interfaz Accesible WCAG AAA |
| Características | Shortcuts teclado, accessible names, contraste alto, navegación por tab, screen reader compatible |
| Descripción del requerimiento | La interfaz debe cumplir estándares WCAG AAA mediante shortcuts de teclado (Ctrl+S guardar, Ctrl+N nuevo, Ctrl+E exportar), accessible names en todos los widgets para lectores de pantalla, contraste de color texto/fondo ratio 12.63:1 (#2c3e50 sobre #ffffff), navegación completa por tab order y compatibilidad con tecnologías asistivas |
| Requerimiento Funcional relacionado | RF-19 (Workflow), RF-10 (Visualización), RF-12 (Tabla Resultados) |
| Prioridad del requerimiento | Media |
| Implementación | Shortcuts en `src/gui/workflows/ast_workflow.py`, setAccessibleName() en todos los widgets, paleta de colores de alto contraste |
| Validación | 37 tests passing en `tests/test_accessibility.py`, navegación completa sin mouse posible |

## RNF-07: Performance

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-07 |
| Nombre del Requerimiento | Tiempo de Respuesta Aceptable |
| Características | Panel 96 wells < 10s, cálculo MIC < 10ms, carga de panel < 100ms, exportación < 2s |
| Descripción del requerimiento | El sistema debe garantizar tiempos de respuesta aceptables: simulación de panel completo de 96 pocillos en menos de 10 segundos (modo estocástico), cálculo individual de MIC en menos de 10 milisegundos (con caché), carga de layout de panel en menos de 100 milisegundos, exportación de resultados a PDF en menos de 2 segundos |
| Requerimiento Funcional relacionado | RF-04 (Simulación), RF-05 (Cálculo MIC), RF-13 (Exportación) |
| Prioridad del requerimiento | Alta |
| Implementación | Vectorización NumPy, caché LRU, connection pooling, batch processing |
| Validación | Medido: Panel 96 wells 5.1s, MIC 0.01ms (cache), throughput 18.7 wells/s |

## RNF-08: Portabilidad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-08 |
| Nombre del Requerimiento | Multiplataforma sin Dependencias Externas |
| Características | Temas nativos (Windows, macOS, Linux), rutas multiplataforma, fuentes sistema, PyQt5 standalone |
| Descripción del requerimiento | El sistema debe ser completamente portable entre Windows, macOS y Linux sin dependencias externas adicionales, utilizando temas nativos (Fusion, Windows Vista, macOS), rutas multiplataforma con pathlib, fuentes del sistema con fallbacks y PyQt5 como único framework GUI sin librerías nativas adicionales |
| Requerimiento Funcional relacionado | RF-13 (Exportación), RF-16 (Persistencia) |
| Prioridad del requerimiento | Alta |
| Implementación | `src/utils/theme_manager.py` (ThemeManager), pathlib.Path en todos los módulos, detección automática de plataforma |
| Validación | 16 tests passing en `tests/test_portability.py`, ejecutable en Windows 10/11, Ubuntu 20.04+, macOS 10.15+ |

## RNF-09: Confiabilidad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-09 |
| Nombre del Requerimiento | Reproducibilidad de Resultados |
| Características | Semilla aleatoria configurable, modo determinista, logging de parámetros, versionado de datos científicos |
| Descripción del requerimiento | El sistema debe garantizar reproducibilidad de resultados mediante semilla aleatoria configurable para simulaciones estocásticas, modo determinista sin variabilidad experimental, logging completo de parámetros de entrada en cada simulación y versionado de datos científicos (breakpoints, multiplicadores) con migraciones trazables |
| Requerimiento Funcional relacionado | RF-18 (Modo Determinista), RF-20 (Carga Datos) |
| Prioridad del requerimiento | Alta |
| Implementación | Parámetro seed en ExperimentalNoiseModel, modo determinista en MechanisticPredictionEngine, migraciones versionadas en src/migrations/ |
| Validación | Simulaciones con misma semilla producen resultados idénticos, migraciones aplicadas en orden correcto |

## RNF-10: Mantenibilidad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-10 |
| Nombre del Requerimiento | Código Mantenible y Documentado |
| Características | Arquitectura en capas, separación de responsabilidades, docstrings Google style, type hints Python 3.8+ |
| Descripción del requerimiento | El código debe ser mantenible mediante arquitectura en capas (Presentation/Core/Data/Utils), separación clara de responsabilidades (Widgets, Workflows, Calculators), docstrings en formato Google style para todas las funciones públicas, type hints Python 3.8+ en todas las firmas de métodos y nomenclatura descriptiva consistente |
| Requerimiento Funcional relacionado | Todos los RF |
| Prioridad del requerimiento | Media |
| Implementación | Estructura modular en src/, docstrings en todos los módulos, type hints verificados con mypy |
| Validación | Código organizado en 4 capas claras, 100% funciones públicas documentadas, type coverage > 80% |

## RNF-11: Escalabilidad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-11 |
| Nombre del Requerimiento | Capacidad de Expansión Científica |
| Características | Diseño extensible para nuevas especies, framework de plugins, esquema BD normalizado, APIs bien definidas |
| Descripción del requerimiento | El sistema debe ser escalable para soportar nuevas especies bacterianas (actualmente P. aeruginosa), nuevos antibióticos, nuevos mecanismos de resistencia y nuevos estándares de interpretación mediante diseño extensible, framework de plugins potencial, esquema de BD normalizado y APIs bien definidas entre capas |
| Requerimiento Funcional relacionado | RF-01 (Identificación), RF-05 (Cálculo MIC), RF-07 (Interpretación) |
| Prioridad del requerimiento | Baja |
| Implementación | Esquema BD genérico (organism field en Breakpoint/BaselineMIC), BreakpointService desacoplado, GenotypePhenotypeCalculator parametrizable |
| Validación | Posible agregar nueva especie modificando solo tablas BD sin cambiar código |

## RNF-12: Trazabilidad

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RNF-12 |
| Nombre del Requerimiento | Trazabilidad Completa de Simulaciones |
| Características | Registro de parámetros input, timestamp de ejecución, versionado de datos, logs estructurados |
| Descripción del requerimiento | El sistema debe mantener trazabilidad completa de todas las simulaciones mediante registro de parámetros de entrada completos (genotipo, panel, modo), timestamp de ejecución, versionado de datos científicos utilizados (breakpoints v15.0, etc.), logs estructurados con niveles INFO/ERROR y almacenamiento persistente de resultados históricos |
| Requerimiento Funcional relacionado | RF-16 (Persistencia), RF-17 (Logging) |
| Prioridad del requerimiento | Media |
| Implementación | Tabla BacteriaProfile con created_at, logs estructurados en error_handler.py, metadatos en exports |
| Validación | Toda simulación trazable a parámetros exactos, logs permiten debugging retroactivo |
