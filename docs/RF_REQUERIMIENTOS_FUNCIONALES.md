# Requerimientos Funcionales (RF)

## RF-01: Identificación de Especie Bacteriana

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-01 |
| Nombre del Requerimiento | Identificación y Configuración de Especie Bacteriana |
| Características | Selección de organismo, origen de muestra, historial de antibióticos previos |
| Descripción del requerimiento | El sistema debe permitir al usuario especificar la especie bacteriana objetivo (Pseudomonas aeruginosa), el origen de la muestra clínica y el historial de exposición a antibióticos previos para contextualizar la simulación |
| Requerimiento NO funcional | RNF-3 (Seguridad - Validación de inputs) |
| Prioridad del requerimiento | Alta |

## RF-02: Generación de Perfil Bacteriano

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-02 |
| Nombre del Requerimiento | Generación In-Silico de Perfiles Bacterianos |
| Características | Generación automática de genotipos, asignación de mutaciones, cálculo de MICs baseline |
| Descripción del requerimiento | El sistema debe generar perfiles bacterianos virtuales con genotipos predefinidos basados en escenarios clínicos (sensible, MDR, XDR), incluyendo la asignación de genes de resistencia y el cálculo automático de MICs para cada antibiótico según el genotipo |
| Requerimiento NO funcional | RNF-4 (Protección - Manejo de errores), RNF-5 (Sostenibilidad - Optimización de cálculos) |
| Prioridad del requerimiento | Alta |

## RF-03: Selección de Panel AST

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-03 |
| Nombre del Requerimiento | Selección y Configuración de Panel AST |
| Características | Visualización de paneles disponibles, selección de layout de 96 pocillos, configuración de antibióticos y concentraciones |
| Descripción del requerimiento | El sistema debe proporcionar paneles AST predefinidos (EUCAST, CLSI) con distribuciones de antibióticos y concentraciones según estándares internacionales, permitiendo al usuario seleccionar el panel apropiado para la simulación |
| Requerimiento NO funcional | RNF-1 (Usabilidad - Interfaz intuitiva), RNF-3 (Seguridad - Validación de selección) |
| Prioridad del requerimiento | Alta |

## RF-04: Simulación de Crecimiento Bacteriano

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-04 |
| Nombre del Requerimiento | Simulación de Curvas de Crecimiento Logístico |
| Características | Modelo logístico de Verhulst, inhibición por antibióticos (ecuación de Hill), ruido experimental multicapa |
| Descripción del requerimiento | El sistema debe simular curvas de crecimiento bacteriano para cada pocillo del panel AST utilizando el modelo logístico, aplicando inhibición antibiótica mediante la ecuación de Hill y agregando ruido experimental realista (instrumental, biológico, wells fallidos) |
| Requerimiento NO funcional | RNF-5 (Sostenibilidad - Vectorización NumPy), RNF-4 (Protección - Validación de parámetros) |
| Prioridad del requerimiento | Alta |

## RF-05: Cálculo de MICs Genotipo-Fenotipo

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-05 |
| Nombre del Requerimiento | Cálculo de MIC Basado en Genotipo |
| Características | Mapeo gen-clase antibiótica, multiplicadores de resistencia, MIC baseline wild-type |
| Descripción del requerimiento | El sistema debe calcular la Concentración Inhibitoria Mínima (MIC) para cada antibiótico basándose en el genotipo bacteriano, aplicando multiplicadores de resistencia específicos para cada combinación gen-clase antibiótica sobre el MIC baseline del wild-type |
| Requerimiento NO funcional | RNF-5 (Sostenibilidad - Caché LRU), RNF-4 (Protección - Manejo de genes desconocidos) |
| Prioridad del requerimiento | Alta |

## RF-06: Determinación Virtual de MIC

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-06 |
| Nombre del Requerimiento | Determinación de MIC desde Curvas de Crecimiento |
| Características | Interpolación de OD, umbral de crecimiento (OD > 0.1), determinación de concentración crítica |
| Descripción del requerimiento | El sistema debe determinar el MIC observado a partir de las curvas de crecimiento simuladas, identificando la menor concentración de antibiótico que inhibe el crecimiento visible (OD final < 0.1) mediante interpolación entre pocillos adyacentes |
| Requerimiento NO funcional | RNF-4 (Protección - Validación de datos), RNF-5 (Sostenibilidad - Algoritmo eficiente) |
| Prioridad del requerimiento | Alta |

## RF-07: Interpretación Según Breakpoints

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-07 |
| Nombre del Requerimiento | Interpretación S/I/R Según Breakpoints Clínicos |
| Características | Breakpoints EUCAST v15.0, breakpoints CLSI M07, categorización S/I/R |
| Descripción del requerimiento | El sistema debe interpretar los valores MIC determinados según los breakpoints clínicos EUCAST y CLSI, clasificando cada antibiótico como Sensible (S), Intermedio (I) o Resistente (R) para Pseudomonas aeruginosa |
| Requerimiento NO funcional | RNF-3 (Seguridad - Validación de breakpoints), RNF-4 (Protección - Manejo de estándares faltantes) |
| Prioridad del requerimiento | Alta |

## RF-08: Simulación Evolutiva

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-08 |
| Nombre del Requerimiento | Motor de Simulación Evolutiva con Mutaciones Adaptativas |
| Características | Mutaciones estocásticas, presión selectiva antibiótica, cálculo de fitness, evolución temporal |
| Descripción del requerimiento | El sistema debe simular la evolución bacteriana bajo presión antibiótica mediante un motor evolutivo que calcule probabilidades de mutación adaptativas (incrementadas por estrés antibiótico), seleccione genes de resistencia aleatoriamente del pool disponible y actualice el genotipo a lo largo de múltiples timesteps |
| Requerimiento NO funcional | RNF-5 (Sostenibilidad - Algoritmo eficiente), RNF-4 (Protección - Validación de parámetros) |
| Prioridad del requerimiento | Media |

## RF-09: Cálculo de Costos de Fitness

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-09 |
| Nombre del Requerimiento | Evaluación de Costos Biológicos de Resistencia |
| Características | Índice competitivo (CI), penalización de tasa de crecimiento, aumento de tiempo de duplicación |
| Descripción del requerimiento | El sistema debe calcular los costos de fitness asociados a mecanismos de resistencia, aplicando un modelo multiplicativo para el índice competitivo y penalizaciones aditivas para la tasa de crecimiento según la literatura científica (PMID: 19258524, 21876761) |
| Requerimiento NO funcional | RNF-5 (Sostenibilidad - Lookup directo BD), RNF-4 (Protección - Valores por defecto) |
| Prioridad del requerimiento | Media |

## RF-10: Visualización de Microplaca

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-10 |
| Nombre del Requerimiento | Visualización Interactiva de Panel 96 Pocillos |
| Características | Representación gráfica 8x12, código de colores por crecimiento, tooltips con datos del pocillo |
| Descripción del requerimiento | El sistema debe proporcionar una visualización gráfica del panel AST de 96 pocillos (formato 8 filas × 12 columnas), con código de colores indicando el nivel de crecimiento bacteriano (verde=crecimiento, rojo=inhibición) y tooltips mostrando antibiótico, concentración y OD al pasar el cursor |
| Requerimiento NO funcional | RNF-1 (Usabilidad - Interfaz intuitiva), RNF-6 (Accesibilidad - Contraste de colores) |
| Prioridad del requerimiento | Media |

## RF-11: Visualización de Curvas de Crecimiento

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-11 |
| Nombre del Requerimiento | Gráficos de Curvas de Crecimiento Temporal |
| Características | Gráficos OD vs tiempo, múltiples concentraciones simultáneas, leyenda con MIC |
| Descripción del requerimiento | El sistema debe generar gráficos de curvas de crecimiento (OD600 vs tiempo) para cada antibiótico, mostrando simultáneamente múltiples concentraciones en un mismo gráfico con líneas diferenciadas y una leyenda indicando el MIC determinado |
| Requerimiento NO funcional | RNF-1 (Usabilidad - Visualización clara), RNF-6 (Accesibilidad - Leyendas descriptivas) |
| Prioridad del requerimiento | Media |

## RF-12: Tabla de Resultados

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-12 |
| Nombre del Requerimiento | Tabla Consolidada de Resultados MIC |
| Características | Columnas: antibiótico, MIC, interpretación, guideline, filtrado por estándar |
| Descripción del requerimiento | El sistema debe presentar los resultados de la simulación AST en formato tabular con columnas para antibiótico, concentración MIC determinada, interpretación clínica (S/I/R), guideline aplicado (EUCAST/CLSI) y permitir filtrado por estándar |
| Requerimiento NO funcional | RNF-1 (Usabilidad - Organización clara), RNF-3 (Seguridad - Validación de datos) |
| Prioridad del requerimiento | Alta |

## RF-13: Exportación de Resultados

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-13 |
| Nombre del Requerimiento | Exportación de Resultados a Formatos Estándar |
| Características | Formatos CSV, Excel, PDF, inclusión de metadatos, firma temporal |
| Descripción del requerimiento | El sistema debe permitir exportar los resultados de la simulación AST a formatos estándar (CSV, XLSX, PDF) incluyendo metadatos (fecha, organismo, perfil bacteriano) y firma temporal para trazabilidad |
| Requerimiento NO funcional | RNF-3 (Seguridad - Validación de rutas), RNF-8 (Portabilidad - Formatos multiplataforma) |
| Prioridad del requerimiento | Media |

## RF-14: Progreso de Simulación

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-14 |
| Nombre del Requerimiento | Indicador de Progreso de Simulación |
| Características | Barra de progreso, tiempo estimado restante, estado actual (generando perfiles, simulando wells, calculando MICs) |
| Descripción del requerimiento | El sistema debe mostrar el progreso de la simulación en tiempo real mediante una barra de progreso con porcentaje completado, tiempo estimado restante y descripción del paso actual siendo ejecutado |
| Requerimiento NO funcional | RNF-1 (Usabilidad - Feedback visual), RNF-4 (Protección - Manejo de cancelación) |
| Prioridad del requerimiento | Baja |

## RF-15: Validación de Entrada

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-15 |
| Nombre del Requerimiento | Validación Integral de Entradas de Usuario |
| Características | Sanitización SQL, validación de rangos numéricos, validación de nombres, validación de rutas de archivo |
| Descripción del requerimiento | El sistema debe validar todas las entradas del usuario antes de procesarlas, incluyendo sanitización contra inyección SQL, verificación de rangos válidos para parámetros numéricos (temperatura 33-37°C, inóculo 5×10⁵-5×10⁶ CFU/mL), validación de nombres de organismos y antibióticos, y verificación de rutas de archivo seguras |
| Requerimiento NO funcional | RNF-3 (Seguridad - InputValidator centralizado) |
| Prioridad del requerimiento | Alta |

## RF-16: Persistencia de Datos

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-16 |
| Nombre del Requerimiento | Almacenamiento Persistente de Datos Científicos |
| Características | Base de datos SQLite, ORM SQLAlchemy 2.0, migraciones versionadas, índices optimizados |
| Descripción del requerimiento | El sistema debe almacenar de forma persistente los datos científicos (breakpoints, multiplicadores MIC, layouts de paneles, perfiles bacterianos) en una base de datos SQLite con ORM SQLAlchemy, aplicando migraciones versionadas automáticamente e índices para optimizar consultas frecuentes |
| Requerimiento NO funcional | RNF-2 (Instalación - Inicialización automática), RNF-5 (Sostenibilidad - Connection pooling) |
| Prioridad del requerimiento | Alta |

## RF-17: Manejo de Errores

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-17 |
| Nombre del Requerimiento | Manejo Robusto de Errores y Logging |
| Características | ErrorHandler centralizado, logging dual (app.log, errors.log), rollback automático BD, decoradores safe_method |
| Descripción del requerimiento | El sistema debe manejar errores de forma robusta mediante un ErrorHandler centralizado que registre eventos en logs duales (INFO general y ERROR crítico), ejecute rollback automático en transacciones fallidas de BD y proporcione decoradores para métodos críticos con valores de fallback |
| Requerimiento NO funcional | RNF-4 (Protección - Error handling), RNF-2 (Instalación - Creación automática de logs) |
| Prioridad del requerimiento | Alta |

## RF-18: Modo Determinista/Estocástico

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-18 |
| Nombre del Requerimiento | Configuración de Modo de Simulación |
| Características | Modo determinista (sin ruido), modo estocástico (ruido realista), control de semilla aleatoria |
| Descripción del requerimiento | El sistema debe permitir ejecutar simulaciones en modo determinista (sin variabilidad experimental, reproducible) o modo estocástico (con ruido instrumental, biológico y wells fallidos), con opción de fijar semilla aleatoria para reproducibilidad de resultados estocásticos |
| Requerimiento NO funcional | RNF-5 (Sostenibilidad - Modo determinista optimizado) |
| Prioridad del requerimiento | Baja |

## RF-19: Workflow Guiado

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-19 |
| Nombre del Requerimiento | Flujo de Trabajo Guiado Paso a Paso |
| Características | Navegación secuencial (Identificación → Perfil → Panel → Simulación → Resultados), validación por etapa, retroalimentación visual |
| Descripción del requerimiento | El sistema debe guiar al usuario a través de un workflow secuencial de 5 etapas (identificación bacteriana, generación de perfil, selección de panel, ejecución de simulación, visualización de resultados) con validación en cada paso y feedback visual del progreso |
| Requerimiento NO funcional | RNF-1 (Usabilidad - Interfaz guiada), RNF-6 (Accesibilidad - Navegación por teclado) |
| Prioridad del requerimiento | Alta |

## RF-20: Carga de Datos Científicos

| Campo | Descripción |
|-------|-------------|
| Identificación de Requerimiento | RF-20 |
| Nombre del Requerimiento | Carga Automática de Datos Científicos Validados |
| Características | Breakpoints EUCAST v15.0 y CLSI M07, matriz gen-clase con referencias PMID, paneles EUCAST/CLSI oficiales, MICs baseline ECOFF |
| Descripción del requerimiento | El sistema debe cargar automáticamente durante la inicialización datos científicos validados incluyendo breakpoints de EUCAST v15.0 y CLSI M07 para P. aeruginosa, matriz de multiplicadores gen-clase con referencias bibliográficas PMID, layouts de paneles oficiales EUCAST/CLSI y MICs baseline wild-type basados en ECOFFs |
| Requerimiento NO funcional | RNF-2 (Instalación - Migraciones automáticas), RNF-5 (Sostenibilidad - Lazy loading) |
| Prioridad del requerimiento | Alta |
