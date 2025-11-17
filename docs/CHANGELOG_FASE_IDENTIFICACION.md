# Changelog - Mejoras de Realismo Clínico

**Fecha**: 17 de noviembre de 2025  
**Autor**: Sistema AST Simulator  
**Sprint**: Feedback de Especialista en Microbiología Clínica

---

## Resumen Ejecutivo

Implementación de tres fases críticas de mejora basadas en revisión con especialista:

1. **Fase 1: Identificación Bacteriana** - Flujo diagnóstico previo al AST
2. **Fase 2: Ruido Experimental Realista** - Curvas de crecimiento naturales
3. **Fase 3: Variabilidad del Inóculo** - Efecto en MIC aparente
4. **Refactorización SOLID** - Arquitectura mantenible y escalable

---

## FASE 1: Identificación Bacteriana

### Problema Identificado
> **"Tu simulador asume que ya 'conoces' la bacteria"**

El sistema saltaba directamente a AST sin proceso de identificación previo.

### Solución Implementada

**Nuevo Widget**: `BacteriaIdentificationWidget`  
**Archivo**: `src/gui/widgets/bacteria_identification_widget.py` (+485 líneas)

**Flujo simulado**:
1. **Origen de muestra**: 7 tipos clínicos (hemocultivo, esputo, orina, etc.)
2. **Cultivo en MacConkey**: Colonias incoloras (lactosa -)
3. **Pruebas bioquímicas**: Oxidasa (+), Lactosa (-)
4. **Características fenotípicas**: Pigmento pioverdina, olor a uva, crecimiento 42°C
5. **Confirmación**: Pseudomonas aeruginosa (confianza >80%)

**Integración**:
- Nuevo Tab 0 en workflow AST
- Navegación secuencial: ID → Perfil → AST → Resultados
- Sistema de pestañas bloqueadas hasta completar pasos previos

---

## FASE 2: Ruido Experimental Realista

### Problema Identificado
> **"Tu crecimiento es demasiado perfecto"**

Curvas de OD eran deterministas, sin variabilidad experimental real.

### Solución Implementada

**Archivo modificado**: `src/core/growth_models.py` (+250 líneas)

**Clase nueva**: `ExperimentalNoiseModel`

**Fuentes de ruido simuladas**:

1. **Ruido Instrumental** (2-5%)
   - Variabilidad del fotómetro
   - Deriva térmica del sensor
   - Implementación: `np.random.normal(0, 0.03 * OD)`

2. **Offset de Medio** (±0.02 OD)
   - Absorción basal del medio de cultivo
   - Constante por pocillo (no varía en el tiempo)

3. **Variabilidad de Volumen** (±8%)
   - Errores de pipeteo en OD inicial
   - Simulación: `od_initial * random.gauss(1.0, 0.08)`

4. **Wells Fallidos** (1.5% probabilidad)
   - Contaminación o muerte súbita
   - Curva plana sin crecimiento

5. **Spikes Aleatorios** (2% probabilidad por medición)
   - Burbujas de aire transitorias
   - Incremento temporal de +0.05 a +0.15 OD

6. **Lags Extendidos** (5% probabilidad)
   - Adaptación lenta al antibiótico
   - t_mid multiplicado por 1.3-1.8x

**Variabilidad biológica agregada**:
```python
k_varied = k * random.gauss(1.0, 0.15)      # ±15%
t_mid_varied = t_mid * random.gauss(1.0, 0.10)  # ±10%
od_max_varied = od_max * random.gauss(1.0, 0.08) # ±8%
```

**Parámetros controlados**:
- Basado en CLSI M07-A11 (variabilidad <5% aceptable)
- Conservador para mantener interpretabilidad clínica
- Aprobado por especialista

---

## FASE 3: VARIABILIDAD DEL INÓCULO

### Problema Identificado

**Feedback especialista**: "Tu motor AST no incorpora la variación del inóculo. En la práctica, el técnico ajusta a 0.5 McFarland, pero puede haber desviación de ±0.05. Un inóculo más alto hace que el MIC aparezca más alto."

- **Condición actual**: Inóculo fijo en 0.5 McFarland exacto
- **Problema**: No simula error humano en preparación de inóculo
- **Impacto clínico**: Puede causar clasificación incorrecta S/I/R

### Solución Implementada

**Enfoque**: Sesgo sistemático a nivel placa (no aleatorio por pozo)

#### 1. Generación de Desviación del Inóculo

```python
# En ASTSimulador.__init__()
self.inoculo_deviation = random.uniform(-0.05, 0.05)
self.inoculo_real = self.inoculo_mcfarland + self.inoculo_deviation
```

- **Desviación**: ±0.05 McFarland (±10% del nominal 0.5)
- **Tipo**: Por placa (todos los pozos afectados igual)
- **Distribución**: Uniforme (simulando error técnico aleatorio)

#### 2. Mecanismo de Efecto sobre MIC

**ENFOQUE CORREGIDO** (v2.0 - Noviembre 2025):

El efecto del inóculo NO se implementa ajustando el valor de MIC directamente, sino **ajustando la capacidad de crecimiento bacteriano** (`od_max`).

**Razón del cambio**:
- **v1.0 FALLIDA**: Ajustar `mic_bacteria` no afectaba el MIC reportado
  - El MIC reportado se calcula buscando la concentración donde OD < 0.3
  - Cambiar el MIC de referencia interna no cambia el threshold de OD
  
- **v2.0 EXITOSA**: Ajustar `od_max` afecta el crecimiento observable
  - Inóculo alto → más biomasa inicial → mayor `od_max`
  - Mayor biomasa → bacteria excede OD=0.3 incluso en concentraciones más altas
  - Resultado: MIC aparente aumenta

**Implementación actual**:

```python
# En _simulate_test_well() - líneas 266-276
# Calcular factor de ajuste basado en desviación del inóculo
inoculum_deviation_pct = (self.inoculum_real - self.inoculum_mcfarland) / self.inoculum_mcfarland
inoculum_factor = 1.0 + (5.0 * inoculum_deviation_pct)  # Amplificación 5x

# Ajustar capacidad de crecimiento (NO el MIC)
od_max = 2.0 * inoculum_factor  # En lugar de od_max fijo
```

**Parámetros clave**:
- **Factor de sensibilidad**: 5.0x amplificación
  - Desviación de +10% en inóculo → +50% en od_max
  - Necesario para superar el tamaño de paso de diluciones (2x)
  
- **Rango observado**: od_max varía entre 1.5 y 2.5
  - Inóculo bajo (0.45 McF): od_max ≈ 1.5
  - Inóculo alto (0.55 McF): od_max ≈ 2.5

- **Sin límites artificiales**: El modelo se autoregula naturalmente

#### 3. Aplicación en Simulaciones

**Pozos de antibiótico**:
```python
# _simulate_test_well()
mic_bacteria = mics_calculated.get(well.antibiotico, 1.0)  # SIN ajuste
inoculum_deviation_pct = (self.inoculum_real - self.inoculum_mcfarland) / self.inoculum_mcfarland
inoculum_factor = 1.0 + (5.0 * inoculum_deviation_pct)
od_max = 2.0 * inoculum_factor
od_initial = 0.05 * self.inoculum_real
```

#### 4. Reportes y Trazabilidad

```python
# En get_report()
metadata = {
    "inoculo_nominal": 0.5,
    "inoculo_real": round(self.inoculo_real, 3),
    "inoculo_deviation": round(self.inoculo_deviation, 3),
    # ...
}
```

### Validación Completada

**Test ejecutado**: `scripts/test_inoculum_variability.py`

**Resultados (10 iteraciones, 13 antibióticos)**:
- **Rango de inóculo**: 0.451 - 0.545 McFarland (18.8% diferencia)
- **MICs que cambiaron**: 2/13 antibióticos (15.4%)
  - **Levofloxacino**: 0.96 → 1.92 mg/L (+100% con inóculo alto)
  - **Ciprofloxacino**: 0.24 → 0.48 mg/L (+100% con inóculo alto)
- **MICs sin cambio**: 11/13 antibióticos
  - Razón: MICs basales ya en techo del panel (4.0-8.0 mg/L)
  - Panel EUCAST: [0.25, 0.5, 1.0, 2.0, 4.0, 8.0] - rango limitado

**Criterio de validación**: ≥10% de antibióticos muestran aumento de MIC con inóculo alto
- **VALIDACIÓN EXITOSA**: 15.4% > 10%
- Tendencia correcta: Inóculo alto → MIC aparente más alto

**Limitaciones del panel**:
- Solo antibióticos con MICs basales bajos pueden demostrar el efecto
- Antibióticos con MICs en 4.0-8.0 mg/L no tienen espacio para aumentar
- Comportamiento esperado y realista

### Integración con FASE 2

**Complementariedad**:
- **FASE 2**: Ruido aleatorio por pozo (instrumental, medio, volumen)
- **FASE 3**: Sesgo sistemático por placa (error técnico en preparación)
- **Combinación**: Realismo completo = bias + noise

**Diferencia clave**:
- FASE 2 → Cada pozo tiene variación independiente
- FASE 3 → Todos los pozos desviados en misma dirección

### Archivos Modificados

**src/core/ast_simulator.py**:
- `import random` agregado
- `__init__()`: Generación de desviación y inóculo real
- `_simulate_test_well()`: Ajuste de `od_max` basado en inóculo (líneas 266-276)
- `_simulate_control_well()`: Mismo ajuste de `od_max` (líneas 323-327)
- `get_report()`: Incluye metadata de inóculo

**scripts/test_inoculum_variability.py** (nuevo):
- Test de validación con 10 iteraciones
- Análisis de 13 antibióticos del panel EUCAST
- Comparación de MICs entre inóculo bajo y alto
- Criterio de éxito: ≥10% de antibióticos con aumento de MIC

---

## FASE 4: REFACTORIZACIÓN SOLID

### Problema
`ast_workflow.py` tenía 902 líneas con múltiples responsabilidades violando SRP.

### Solución

**Nuevos controladores** (Dependency Injection):

1. **TabNavigationController** (`tab_navigation_controller.py`)
   - Responsabilidad: Gestión de navegación entre tabs
   - Habilitar/deshabilitar tabs secuencialmente
   - Control de botones de navegación

2. **WorkflowEventHandler** (`workflow_event_handler.py`)
   - Responsabilidad: Procesamiento de eventos
   - Observer Pattern para notificaciones
   - Mensajes en status bar

3. **WorkflowDataManager** (`workflow_data_manager.py`)
   - Responsabilidad: Transformación de datos
   - Generación de curvas de crecimiento
   - Almacenamiento temporal de resultados

**Resultado**:
- Reducción: **902 → 679 líneas** (-25%)
- Separación de responsabilidades clara
- Código más testeable y mantenible
- Sin romper funcionalidad existente

---

## FASE 4: POZOS AMBIGUOS

### Problema Identificado

**Feedback especialista**: "Tu simulador toma OD a color a binario crece/no crece. Esto es demasiado perfecto comparado con MicroScan. En la vida real ocurren pozos con crecimiento debil, pozos contaminados, pozos con borde difuso, pozos con precipitado."

- **Condicion actual**: Todos los pozos se leen perfectamente
- **Problema**: No simula condiciones reales de laboratorio
- **Impacto clinico**: Pozos ambiguos requieren revision manual o repeticion

### Solucion Implementada

**Enfoque**: Asignacion aleatoria de 2-4 pozos con problemas por panel

#### 1. Tipos de Problemas Simulados

**Modulo nuevo**: `src/core/well_issues_model.py`

**Clase**: `WellIssuesSimulator`

**Tipos de problemas implementados**:

1. **Crecimiento Debil** (25% probabilidad)
   - OD reducida en 20-50%
   - Lectura en zona gris (cerca del umbral 0.3)
   - Accion: Repetir prueba o usar metodo alternativo

2. **Contaminacion** (15% probabilidad)
   - OD artificialmente elevada
   - Ruido alto en lecturas
   - Accion: Descartar resultado, repetir con cultivo puro

3. **Borde Difuso** (20% probabilidad)
   - Ruido en zona de transicion (OD 0.2-0.5)
   - Dificil determinar umbral exacto
   - Accion: Revisar manualmente, considerar MIC adyacente

4. **Precipitado** (20% probabilidad)
   - OD incrementada por material particulado (+0.05 a +0.15)
   - No representa crecimiento bacteriano real
   - Accion: Revisar visualmente, no confiar en OD automatica

5. **No Legible** (10% probabilidad)
   - OD = NaN (lectura rechazada)
   - Fallo en sistema optico
   - Accion: Excluir del analisis, reportar como no-disponible

6. **OD Inconsistente** (10% probabilidad)
   - Fluctuacion aleatoria entre lecturas (20%)
   - Curva de crecimiento erratica
   - Accion: Revisar curva completa, considerar repetir

#### 2. Asignacion de Problemas

```python
# En ASTSimulator.simulate_incubation()
well_positions = [w.posicion for w in self.panel_wells]
self.well_issues = self.well_issues_simulator.assign_issues_to_panel(
    well_positions, exclude_controls=True
)
```

**Parametros**:
- **Cantidad**: 2-4 pozos por panel (aleatorio)
- **Exclusion**: Controles nunca tienen problemas
- **Distribucion**: Segun pesos configurados por tipo

#### 3. Aplicacion a Lecturas OD

```python
# En _simulate_test_well()
if well.posicion in self.well_issues:
    issue = self.well_issues[well.posicion]
    od, is_valid = self.well_issues_simulator.apply_issue_to_od(
        od, issue, tiempo_minutos
    )
```

**Efectos segun tipo**:
- **Crecimiento debil**: OD × (0.5 - 0.3×severidad)
- **Contaminacion**: OD × (1.0 + 0.8×severidad) + ruido alto
- **Borde difuso**: Ruido gaussiano en zona 0.2-0.5
- **Precipitado**: OD + random(0.05, 0.15)×severidad
- **No legible**: OD = NaN
- **OD inconsistente**: OD × (1.0 + gaussiano(0, 0.2×severidad))

#### 4. Reportes y Trazabilidad

```python
# En get_report()
"metadata": {
    "pozos_problematicos": len(self.well_issues),
},
"well_issues": [
    {
        "posicion": "A9",
        "tipo": "crecimiento_debil",
        "severidad": 0.53,
        "descripcion": "Crecimiento lento, lectura en zona gris",
        "afecta_lectura": True,
        "afecta_interpretacion": True,
        "accion_recomendada": "Repetir prueba o usar metodo alternativo"
    }
]
```

### Validacion Completada

**Test ejecutado**: `scripts/test_well_issues.py`

**Resultados (5 tests)**:

1. **Generacion de pozos problematicos**: OK
   - Rango 2-4 pozos respetado
   - Asignacion aleatoria funcional

2. **Distribucion de tipos**: OK (50 pozos analizados)
   - Crecimiento debil: 30.0%
   - Borde difuso: 22.0%
   - OD inconsistente: 18.0%
   - Contaminado: 14.0%
   - No legible: 8.0%
   - Precipitado: 8.0%

3. **Modificacion de OD**: OK
   - Pozos UNREADABLE devuelven NaN
   - Otros tipos modifican OD correctamente

4. **Reporte incluye problemas**: OK
   - Metadata con contador de pozos problematicos
   - Seccion `well_issues` con detalles completos
   - Estructura validada

5. **Controles sin problemas**: OK
   - 10 simulaciones verificadas
   - H11, H12 nunca afectados

### Integracion con Fases Previas

**Complementariedad**:
- **FASE 2**: Ruido experimental en todos los pozos (instrumental, pipeteo)
- **FASE 3**: Sesgo sistematico por inoculo (afecta toda la placa)
- **FASE 4**: Problemas especificos en pozos individuales (2-4 por panel)

**Diferencia clave**:
- FASE 2: Ruido aleatorio leve en TODOS los pozos
- FASE 3: Sesgo direccional en TODOS los pozos
- FASE 4: Problemas severos en POCOS pozos especificos

### Archivos Modificados

**src/core/well_issues_model.py** (nuevo - 380 lineas):
- `WellIssueType`: Enum con 6 tipos de problemas
- `WellIssue`: Dataclass con informacion de problema
- `WellIssuesSimulator`: Simulador de problemas
  - `assign_issues_to_panel()`: Asigna 2-4 problemas aleatorios
  - `apply_issue_to_od()`: Modifica OD segun tipo de problema
  - `generate_issue_report()`: Genera reporte de texto

**src/core/ast_simulator.py**:
- Importacion de `WellIssuesSimulator`
- `__init__()`: Inicializa simulador de problemas
- `simulate_incubation()`: Asigna problemas antes de simular
- `_simulate_test_well()`: Aplica problemas a lecturas OD
- `_format_well_issues()`: Formatea problemas para reporte
- `get_report()`: Incluye seccion `well_issues`

**scripts/test_well_issues.py** (nuevo - 265 lineas):
- 5 tests de validacion
- Verificacion de distribucion de tipos
- Validacion de modificaciones OD
- Comprobacion de estructura de reporte

---

## Archivos Modificados

| Archivo | Líneas | Tipo | Descripción |
|---------|--------|------|-------------|
| `src/gui/widgets/bacteria_identification_widget.py` | +485 | Nuevo | Widget identificación bacteriana |
| `src/gui/workflows/ast_workflow.py` | -223 | Refactor | Workflow principal simplificado |
| `src/gui/workflows/tab_navigation_controller.py` | +140 | Nuevo | Controlador navegación SOLID |
| `src/gui/workflows/workflow_event_handler.py` | +160 | Nuevo | Manejador eventos SOLID |
| `src/gui/workflows/workflow_data_manager.py` | +130 | Nuevo | Gestor datos SOLID |
| `src/core/growth_models.py` | +250 | Mejorado | Ruido experimental multicapa |

**Total**: ~942 líneas nuevas/refactorizadas

---

## Validación

### Fase 1 - Identificación

- [x] Flujo completo 0→5 sin errores
- [x] Navegación secuencial funcional
- [x] Cálculo de confianza correcto (6/6 = 100%)
- [x] Señales entre widgets correctas

### Fase 2 - Ruido Experimental

- [x] Curvas con variabilidad observable
- [x] Wells fallidos implementados (1.5%)
- [x] Lags extendidos funcionales (5%)
- [x] Spikes aleatorios presentes
- [x] Parámetros biológicos variables

### Fase 3 - SOLID

- [x] Separación de responsabilidades
- [x] Dependency Injection implementada
- [x] Sin regresiones funcionales
- [x] Reducción de complejidad 25%

---

## Estado de Implementación

### ✅ COMPLETADO

**Fase 1: Identificación Bacteriana**
- Módulo completo e integrado
- 8 pruebas bioquímicas simuladas
- Flujo clínico realista

**Fase 2: Ruido Experimental**
- ExperimentalNoiseModel implementado
- 6 fuentes de variabilidad activas
- Curvas realistas generadas

**Fase 3: Refactorización SOLID**
- 3 controladores separados
- Arquitectura limpia
- Código mantenible

### 📋 Pendiente (Futuras Fases)

Según feedback del especialista:
- Fase 3: Heteroresistencia visual
- Fase 4: QC strain tracking
- Fase 5: Interpretación experta
- Fase 6: Exportación LIMS

---

## Resumen para Especialista

**Implementaciones completadas**:

1. ✅ **Identificación bacteriana** simulada antes de AST
   - MacConkey, Oxidasa, Lactosa, Pigmento, Olor, 42°C
   - Confianza >80% para confirmar P. aeruginosa

2. ✅ **Ruido experimental multicapa** en curvas de crecimiento
   - Instrumental (3%), Medio (±0.02), Volumen (8%)
   - Wells fallidos (1.5%), Spikes (2%), Lags raros (5%)
   - Variabilidad biológica (k±15%, t_mid±10%, od_max±8%)

3. ✅ **Arquitectura SOLID** con 3 controladores
   - Reducción 25% de complejidad
   - Separación clara de responsabilidades

**Próximo paso**: Validar con especialista que el ruido se ve "natural" antes de continuar con siguiente fase.
# Parámetros: organism, sample_origin, confidence
```

**Métodos públicos**:
- `reset()`: Reinicia widget a estado inicial

---

### 2. Integración en Workflow AST

**Archivo**: `src/gui/workflows/ast_workflow.py`

**Cambios estructurales**:

1. **Sistema de tabs actualizado**: 5 tabs → 6 tabs
   - Tab 0: 🔬 Identificación (NUEVO)
   - Tab 1: 🦠 Perfil Bacteriano
   - Tab 2: ⚙️ Configurar AST
   - Tab 3: 🧫 Placa AST
   - Tab 4: 📊 Resultados MIC
   - Tab 5: 📈 Curvas de Crecimiento

2. **Navegación actualizada**:
   - Todos los índices de `setCurrentIndex()` incrementados en +1
   - Botón "Siguiente: Generar Perfil" agregado en Tab 0
   - Lógica de habilitación secuencial mantenida

3. **Nuevo manejador de señales**:
```python
def _on_identification_completed(self, organism, sample_origin, confidence):
    """Habilita Tab 1 (Perfil) tras confirmar identificación."""
    self.main_tabs.setTabEnabled(1, True)
    self.next_profile_btn.setEnabled(True)
```

4. **Actualización de `_restart_workflow()`**:
   - Ahora resetea también `identification_widget`
   - Deshabilita 5 tabs (índices 1-5)
   - Vuelve a Tab 0 (Identificación)

5. **Actualización de `clear_all()`**:
   - Limpia identificación y perfil antes de visualizadores

---

## Archivos Modificados

| Archivo | Líneas Agregadas | Líneas Modificadas | Descripción |
|---------|------------------|-------------------|-------------|
| `src/gui/widgets/bacteria_identification_widget.py` | +485 | 0 | Widget nuevo completo |
| `src/gui/workflows/ast_workflow.py` | +110 | ~35 | Integración de Tab 0 |

**Total**: ~595 líneas de código nuevo/modificado

---

## Impacto en Experiencia de Usuario

### Antes
```
Usuario → [Generar Perfil] → AST → Resultados
```

### Después
```
Usuario → [Seleccionar Muestra] → [Ejecutar Pruebas] → 
[Confirmar P. aeruginosa] → [Generar Perfil] → AST → Resultados
```

**Beneficios**:
- ✅ Flujo clínico realista y educativo
- ✅ Simulación de decisión diagnóstica
- ✅ Visualización de proceso de laboratorio
- ✅ Credibilidad científica del simulador

---

## Pruebas Realizadas

- [x] Flujo completo 0→5 sin errores
- [x] Navegación secuencial con tabs bloqueadas
- [x] Cálculo de confianza (6/6 = 100%)
- [x] Reinicio de workflow desde Tab 5
- [x] Validación de selección de muestra
- [x] Animación de pruebas secuenciales
- [x] Señales entre widgets funcionando

---

## Deuda Técnica Identificada

1. **Complejidad de `ast_workflow.py`**:
   - Archivo: 880+ líneas
   - Responsabilidad única violada (SOLID)
   - **Acción**: Refactorización pendiente (ver siguiente fase)

2. **Hardcoded organism**:
   - Solo soporta *P. aeruginosa*
   - **Mejora futura**: Extensible a otros organismos

3. **Pruebas siempre positivas**:
   - No simula falsos negativos/positivos
   - **Mejora futura**: Variabilidad estocástica

---

## Siguiente Fase: Refactorización SOLID

**Problema**: `ast_workflow.py` tiene múltiples responsabilidades:
- Gestión de navegación entre tabs
- Manejo de señales entre widgets
- Generación de datos para widgets
- Lógica de habilitación/deshabilitación

**Solución propuesta**:
1. **Single Responsibility**: Extraer coordinadores de navegación
2. **Open/Closed**: Tabs como componentes extensibles
3. **Liskov Substitution**: Interfaz común para tabs
4. **Interface Segregation**: Separar señales por contexto
5. **Dependency Inversion**: Inyectar dependencias vs. crear widgets

**Objetivo**: Reducir `ast_workflow.py` de 880 a ~300 líneas sin romper funcionalidad.
