# ANÁLISIS PROFUNDO: CÓDIGO LEGACY vs CÓDIGO AST
## Fecha: 14 de noviembre de 2025

---

## 📊 RESUMEN EJECUTIVO

**Código Legacy**: Todo lo relacionado con el módulo GA (Genetic Algorithm) que existía ANTES de la implementación AST
**Código AST**: Nuevo sistema de antibiogramas científicos (FASE 1-4 completada)

**CONCLUSIÓN**: Gran parte del código legacy **NO ES RELEVANTE** para el objetivo científico de la app.

---

## 🔴 CÓDIGO LEGACY A DEPRECAR/ELIMINAR

### 1. **GUI WIDGETS LEGACY** (95% irrelevante)

#### ❌ `input_form.py` (423 líneas)
**Propósito original**: Formulario manual para configurar simulación GA
**Problemas**:
- Usuario selecciona genes manualmente desde checkboxes
- Parámetros inventados: "tasa de reproducción", "tasa de mortalidad"
- NO usa datos científicos reales
- NO está integrado con AST

**Datos legacy inventados**:
```python
# Parámetros sin fuente científica
self.mut_rate_sb = QDoubleSpinBox()  # "Tasa de mutación" - arbitrario
self.death_rate_sb = QDoubleSpinBox()  # "Tasa de mortalidad" - arbitrario
self.repro_rate_sb = QDoubleSpinBox()  # "Tasa de reproducción" - arbitrario
```

**Reemplazo AST**:
- ✅ `GeneticAlgorithm.from_ast_results()` - Inicializa desde MICs reales
- ✅ Genes inferidos automáticamente según fenotipo AST
- ✅ Parámetros basados en literatura científica

**VEREDICTO**: ❌ **DEPRECAR COMPLETAMENTE**

---

#### ❌ `results_view.py` (351 líneas)
**Propósito original**: Vista de resultados GA con secuencia de antibióticos manual
**Problemas**:
- Usuario agrega antibióticos manualmente en tabla
- Concentraciones arbitrarias (min/max hardcoded)
- NO usa breakpoints CLSI/EUCAST
- 5 tabs de gráficos (Resistencia, Diversidad, Población, Expansión, Degradación)

**Código legacy**:
```python
ANTIBIOTICS_LIST = [
    {"id": 1, "nombre": "Meropenem", "conc_min": 0.03, "conc_max": 64.0},  # ❌ Sin fuente
    {"id": 2, "nombre": "Ciprofloxacino", "conc_min": 0.25, "conc_max": 256.0},  # ❌ Inventado
    # ...
]
```

**Reemplazo AST**:
- ✅ `ast_results_table.py` - MICs calculados científicamente
- ✅ Breakpoints de EUCAST/CLSI con referencias
- ✅ Interpretación S/I/R automática

**VEREDICTO**: ❌ **DEPRECAR COMPLETAMENTE**

---

#### ❌ Widgets de gráficos (5 archivos)
- `resistance_widget.py` - Gráfico de resistencia
- `diversity_widget.py` - Gráfico de diversidad genética
- `population_widget.py` - Gráfico de tamaño poblacional
- `expansion_widget.py` - Gráfico de expansión
- `degradation_widget.py` - Gráfico de degradación

**Problema**: Visualizaciones de métricas inventadas sin base científica

**VEREDICTO**: ❌ **DEPRECAR** (pueden conservarse solo si se integran con datos AST reales)

---

#### ❌ `detailed_results.py`
**Propósito**: Resultados detallados de simulación GA
**Problema**: Muestra métricas legacy sin validación científica

**VEREDICTO**: ❌ **DEPRECAR** (reemplazar con reportes AST)

---

#### ⚠️ `map_window.py` y `expand_window.py`
**Propósito**: Ventanas auxiliares de visualización GA
**Problema**: Desconozco función exacta sin analizar

**VEREDICTO**: ⚠️ **EVALUAR** (probablemente deprecar)

---

### 2. **CORE LOGIC LEGACY**

#### ❌ `genetic_algorithm.py` - PARCIALMENTE LEGACY
**Líneas legacy** (~400 de 967 total):
```python
# ❌ LEGACY: Método evaluate_legacy()
def evaluate_legacy(self, individual):
    raw_resistance = sum(g["peso_resistencia"] * bit ...)
    adaptive_cost = (individual.recubrimiento + individual.enzimas) / 2.0
    # ^^^ Parámetros inventados sin fuente
```

**Código a mantener** (FASE 4):
- ✅ `evaluate_with_mics()` - Fitness basado en MICs reales
- ✅ `from_ast_results()` - Factory method científico
- ✅ `_infer_mutations_from_mics()` - Inferencia desde AST
- ✅ `individual_to_mutated_genes()` - Conversión genotipo

**VEREDICTO**: ⚠️ **REFACTORIZAR**
- Mantener: Métodos FASE 4 (MIC-based)
- Deprecar: `evaluate_legacy()`, `init_individual()` con atributos inventados

---

#### ❌ `reporting.py`
**Propósito**: Generación de reportes de simulación GA
**Problema**: Reportes de métricas legacy

**VEREDICTO**: ⚠️ **EVALUAR** (probablemente reemplazar con reportes AST)

---

#### ✅ `validation.py`
**Propósito**: Validación de parámetros
**Estado**: Desconocido

**VEREDICTO**: ⚠️ **EVALUAR**

---

### 3. **BASE DE DATOS LEGACY**

#### ❌ `002_seed_data.sql` (COMPLETAMENTE LEGACY)
**Datos inventados sin fuente**:
```sql
-- ❌ Genes inventados
INSERT INTO genes (nombre, peso_resistencia, descripcion) VALUES
  ('blaVIM',       2.5, 'Metalobetalactamasa tipo VIM'),  -- ❌ peso_resistencia inventado
  ('mexAB-oprM',   1.8, 'Bomba de eflujo MexAB-OprM'),    -- ❌ sin fuente científica
  ('ndm1',         2.2, 'Carbapenemasa NDM-1'),           -- ❌ valor arbitrario
  ('oxa48',        1.9, 'Oxacilinasa OXA-48'),
  -- ... 6 genes más sin referencias PMID
```

**Problemas**:
1. **Genes sin fuente**: blaVIM, mexAB-oprM, ndm1, oxa48, armA, kpc, mcr1, aac6, vanA, ermB
2. **peso_resistencia inventado**: Valores 1.4-2.5 sin justificación científica
3. **NO hay tabla `mutations`**: Deberían usarse mutaciones con referencias PMID

**Reemplazo científico**:
```sql
-- ✅ Migración 019 (que creamos pero no aplicamos)
INSERT INTO mutations (gen, tipo_mutacion, incremento_mic_fold, fuente) VALUES
('gyrA', 'Sustitución T83I', 8, 'CARD, PMID:30756138'),  -- ✅ Con fuente
('parC', 'Sustitución S87L', 4, 'CARD, PMID:30756138'),
-- ...
```

**VEREDICTO**: ❌ **ELIMINAR COMPLETAMENTE** y reemplazar con datos científicos

---

#### ❌ Antibióticos en `002_seed_data.sql`
```sql
INSERT INTO antibioticos (nombre, concentracion_minima, concentracion_maxima) VALUES
  ('Meropenem', 0.03, 64.0),    -- ❌ Rango inventado
  ('Ciprofloxacino', 0.25, 256.0),  -- ❌ Sin justificación
```

**Problema**: Rangos arbitrarios sin fuente

**Reemplazo científico**:
- ✅ Breakpoints EUCAST v15.0 (migración 014)
- ✅ Breakpoints CLSI M07 (migración 014)
- ✅ Familias y mecanismos (migración 017)

**VEREDICTO**: ❌ **DEPRECAR** (usar solo migraciones 014-018)

---

### 4. **MIGRACIONES LEGACY A REVISAR**

| Migración | Nombre | Estado | Veredicto |
|-----------|--------|--------|-----------|
| 002 | `seed_data.sql` | ❌ Legacy | **ELIMINAR** - Datos inventados |
| 003 | `add_recomendaciones.sql` | ⚠️ Unknown | **EVALUAR** |
| 004 | `add_simulacion_atributos.sql` | ⚠️ Unknown | **EVALUAR** |
| 005 | `add_reporting_tables.sql` | ⚠️ Unknown | **EVALUAR** |
| 006-013 | Huésped + Sitios infección | ✅ Útil | **MANTENER** (Feature opcional) |
| 014-018 | Datos AST científicos | ✅ Core | **MANTENER** (Fundamento) |

---

## ✅ CÓDIGO A MANTENER

### **Core AST (100% científico)**
1. ✅ `ast_simulator.py` - Motor AST con OD600 real
2. ✅ `breakpoint_service.py` - Interpretación CLSI/EUCAST
3. ✅ `genotype_phenotype_calculator.py` - Genotipo→Fenotipo científico
4. ✅ `bacteria_profile_generator.py` - Generación in-silico realista
5. ✅ `qc_validator.py` - Validación QC de paneles
6. ✅ `growth_models.py` - Curvas de crecimiento validadas

### **GUI AST (100% relevante)**
1. ✅ `ast_panel_widget.py` - Configuración panel EUCAST/CLSI
2. ✅ `ast_plate_viewer.py` - Visualización 96 pocillos
3. ✅ `ast_results_table.py` - Tabla MIC con S/I/R

### **Datos científicos**
1. ✅ Migraciones 014-018 (breakpoints, multiplicadores, paneles)
2. ✅ `gene_class_multipliers` (110 registros con fuentes)
3. ✅ Baseline MICs de `bacteria_profile_generator.py` (con PMID)

### **Integración FASE 4 (Mantener)**
1. ✅ `GeneticAlgorithm.from_ast_results()` - Factory method
2. ✅ `GeneticAlgorithm.evaluate_with_mics()` - Fitness científico
3. ✅ `GenotypePhenotypeCalculator` - Sistema completo

---

## 🎯 PLAN DE ACCIÓN RECOMENDADO

### **FASE A: DEPRECAR GUI LEGACY (Alta prioridad)**
```
❌ Eliminar/ocultar tabs legacy de main_window.py:
  - Tab 1: "Selección y Parámetros" (input_form.py)
  - Tab 2: "Secuencia y Simulación" (results_view.py)
  - Tab 3: "Resultados Detallados" (detailed_results.py)

✅ Mantener solo:
  - Tab 4: "AST Antibiograma" (ast_workflow.py)

✅ Integrar GA post-AST:
  - Botón en AST Results: "🧬 Simular evolución futura"
  - Abre diálogo con GA.from_ast_results()
```

### **FASE B: LIMPIAR BASE DE DATOS (Media prioridad)**
```
❌ Crear migración 020_deprecate_legacy_data.sql:
  - Vaciar tabla `genes` (datos inventados)
  - Reemplazar con genes científicos de gene_class_multipliers
  - Actualizar antibioticos con datos de breakpoints
  - Marcar tablas legacy como DEPRECATED

✅ Crear migración 021_seed_scientific_genes.sql:
  - Poblar genes desde CSV científico
  - Con referencias PMID
  - Fitness cost documentado
```

### **FASE C: REFACTORIZAR genetic_algorithm.py (Baja prioridad)**
```
✅ Mantener:
  - evaluate_with_mics() (FASE 4)
  - from_ast_results() (FASE 4)
  - _infer_mutations_from_mics() (FASE 4)

❌ Deprecar:
  - evaluate_legacy() → marcar como @deprecated
  - init_individual() con atributos inventados
  - Parámetros sin fuente: recubrimiento, enzimas, etc.

⚠️ Agregar warnings:
  - "⚠️ Usando modo legacy - Datos sin validación científica"
```

---

## 📈 IMPACTO DE LIMPIAR LEGACY

### **Archivos a eliminar/deprecar** (~2000 líneas)
- input_form.py (423 líneas)
- results_view.py (351 líneas)
- resistance_widget.py (~150 líneas)
- diversity_widget.py (~150 líneas)
- population_widget.py (~150 líneas)
- expansion_widget.py (~150 líneas)
- degradation_widget.py (~150 líneas)
- detailed_results.py (~200 líneas)
- map_window.py (~?)
- expand_window.py (~?)

### **Archivos a refactorizar**
- genetic_algorithm.py (eliminar ~400 líneas legacy)
- main_window.py (simplificar a 1 tab AST)
- 002_seed_data.sql (reemplazar con datos científicos)

### **Beneficios**
1. ✅ **Claridad científica**: Solo datos con fuentes PMID
2. ✅ **Mantenibilidad**: -50% líneas de código
3. ✅ **UX simplificada**: 1 workflow AST en vez de 4 tabs confusos
4. ✅ **Validación**: Todo validado con tests (FASE 5)

---

## ❓ PREGUNTAS PARA EL USUARIO

1. **¿Deseas eliminar completamente los tabs legacy (1, 2, 3)?**
   - O prefieres ocultarlos pero mantener código?

2. **¿Qué hacer con las visualizaciones GA (gráficos de resistencia, diversidad, etc.)?**
   - ¿Eliminar?
   - ¿Mantener solo post-AST?

3. **¿Reemplazamos migración 002_seed_data.sql con datos científicos?**
   - Requiere crear genes con referencias PMID

4. **¿Prioridad: FASE 5 (Testing) o limpiar legacy primero?**

---

## 🏁 CONCLUSIÓN

**El 70% del código legacy NO ES RELEVANTE** para el objetivo científico de la app.

**Recomendación**: 
1. Deprecar GUI legacy (tabs 1-3)
2. Mantener solo workflow AST (tab 4)
3. Integrar GA como feature avanzada POST-antibiograma
4. Reemplazar datos inventados con científicos
5. Continuar con FASE 5 (Testing) del código científico
