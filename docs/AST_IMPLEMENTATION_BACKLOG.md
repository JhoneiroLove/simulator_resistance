# BACKLOG DE IMPLEMENTACIÓN - MÓDULO AST
## Simulador de Resistencia Bacteriana (SRB)

**Fecha de creación**: 9 de noviembre de 2025  
**Última actualización**: 11 de noviembre de 2025  
**Objetivo**: Refactorizar aplicación + Implementar workflow AST completo para microbiólogos  
**Estado**: 🟡 EN PROGRESO (25% completado - 7/28 items)

---

## 📝 RESUMEN EJECUTIVO - VISIÓN DEL PROYECTO

**SÍ, ES REFACTORIZACIÓN + EXPANSIÓN**. El proyecto actual tiene un módulo GA (Genetic Algorithm) que simula evolución bacteriana, pero **NO tiene un flujo de trabajo clínico completo** para microbiólogos. La refactorización consistirá en **transformar la aplicación en un simulador de laboratorio de microbiología clínica** con flujo completo:

### 🔬 **Flujo de Trabajo Clínico (Usuario: Microbiólogo)**

**IMPORTANTE**: UX/UI propia (inspirada en MicroScan, NO copia exacta)

```
┌─────────────────────────────────────────────────────────────────┐
│  PASO 1: Inicio de Simulación                                  │
│  → Usuario indica origen: "Hemocultivo" / "Esputo" / "Orina"   │
│  → Disclaimer: "Bacteria: P. aeruginosa (pre-identificada)"    │
│  → Botón: "Comenzar Antibiograma →"                            │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASO 2: Selección de Antibióticos (SIMPLE)                    │
│  → Opción A: ○ Panel Estándar (12 antibióticos) [Recomendado] │
│  → Opción B: ○ Personalizado (checklist)                       │
│  → Si personalizado: ☑ Meropenem ☑ Ciprofloxacino ☐ ...       │
│  → Sistema NO muestra concentraciones (automáticas)            │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASO 3: Parámetros de Simulación (SIMPLE)                     │
│  → Inóculo: [0.5] McFarland (dropdown: 0.3/0.5/0.7)           │
│  → Temperatura: [37°C] (fijo, mostrar como info)               │
│  → Duración: [18h] (fijo, estándar AST)                        │
│  → ℹ️ Panel y concentraciones: automáticos                     │
│  → NO hay "vista previa 96 pocillos" (demasiado técnico)      │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASO 4: Incubación Simulada (Visualización Amigable)          │
│  → Simulación en tiempo acelerado (18h real → 20-30 seg)       │
│  → Barra de progreso con mensaje: "Simulando hora 6 de 18..."  │
│  → [OPCIONAL] Mini-gráfico: curvas de crecimiento en vivo      │
│  → NO mostrar grid 96 pocillos aquí (abrumador)                │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASO 5: Visualización de Resultados - Grid 96 Pocillos        │
│  → Grid 8×12 con colores según turbidez:                       │
│    🟩 Verde (claro) | 🟨 Amarillo (ligero) | 🟧 Naranja (turbio)│
│  → Tooltip al pasar mouse: "A1: Meropenem 0.5 µg/mL, OD=0.15" │
│  → Controles QC destacados: H11 ✅, H12 ✅                      │
│  → Slider temporal: "Ver placa en hora: [18] (0-18h)"          │
│  → Diseño propio (NO copiar MicroScan, inspirarse)             │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASO 6: Tabla de Resultados MIC (SIMPLE Y CLARA)              │
│  → Tabla con 4 columnas esenciales:                            │
│    | Antibiótico | MIC (µg/mL) | S/I/R | Guideline |           │
│    | Meropenem   | 2.0         | 🟢 S  | CLSI      |           │
│    | Ciproflox.  | ≥64         | 🔴 R  | CLSI      |           │
│  → Colores: 🟢 Verde (S), 🟡 Amarillo (I), 🔴 Rojo (R)        │
│  → NO mostrar breakpoints aquí (demasiado técnico para MVP)    │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  PASO 7: Antibiograma Final (Reporte)                          │
│  → Resumen ejecutivo:                                           │
│    - Organismo: P. aeruginosa                                   │
│    - Fecha: 2025-11-09                                          │
│    - Sensibles: 8/12 antibióticos                               │
│    - Resistentes: 4/12                                          │
│  → Botones:                                                     │
│    [Exportar PDF] [Exportar CSV] [Guardar Sesión]             │
│  → [OPCIONAL] "🧬 ¿Simular evolución?" → Abre módulo GA       │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 **Refactorización Necesaria**

#### **GUI (Interfaz de Usuario)**
- ❌ **Eliminar**: Tabs separados "GA" y "AST" como módulos independientes
- ✅ **Crear**: Wizard paso a paso (QWizard) o Stepper vertical
- ✅ **Crear**: Navegación secuencial: Anterior / Siguiente / Finalizar
- ✅ **Integrar**: Módulo GA como feature avanzada post-antibiograma

#### **Lógica de Negocio**
- ✅ **Mantener**: Módulo GA existente (genetic_algorithm.py)
- ✅ **Crear**: Módulo AST nuevo (ast_simulator.py, breakpoint_service.py, etc.)
- ✅ **Crear**: Servicio de workflow (workflow_manager.py) que coordine pasos
- ✅ **Integrar**: GA se ejecuta DESPUÉS del antibiograma (simular resistencia futura)

#### **Base de Datos**
- ✅ **Crear**: 8 nuevas tablas AST (panel_layouts, ast_runs, ast_wells, etc.)
- ✅ **Relacionar**: Tabla `simulacion` (GA) con `ast_runs` (AST) mediante foreign key
- ✅ **Crear**: Tabla `workflow_sessions` (guardar progreso del usuario)

---

## 🎯 OBJETIVO GENERAL

Implementar un módulo completo de **AST (Antimicrobial Susceptibility Testing)** que simule el funcionamiento del MicroScan **SIMPLIFICADO**, incluyendo:

### ✅ LO QUE SÍ SIMULAREMOS (Basado en MicroScan)
- ✅ Paneles de microdilución con pocillos (96 wells)
- ✅ Medición de crecimiento bacteriano (turbidez simulada OD600)
- ✅ Cálculo de MIC (Minimum Inhibitory Concentration)
- ✅ Interpretación S/I/R según breakpoints CLSI/EUCAST
- ✅ Sistema de control de calidad (QC) - controles positivo/negativo
- ✅ Integración opcional con módulo GA existente

### ❌ LO QUE NO SIMULAREMOS (Fuera de alcance)
- ❌ Recolección de muestra clínica (sangre, orina, esputo)
- ❌ Identificación bacteriana (MALDI-TOF, API, Vitek ID)
- ❌ Múltiples especies (solo **Pseudomonas aeruginosa**)
- ❌ Tinción de Gram
- ❌ Pruebas bioquímicas
- ❌ Detección de mecanismos de resistencia (PCR, genes)

### 🔬 ALCANCE ESPECÍFICO
**Organismo fijo**: *Pseudomonas aeruginosa*  
**Punto de partida**: Cultivo puro aislado (asumido)  
**Proceso simulado**: Panel de AST → Incubación → Lectura → MIC → S/I/R  
**Salida**: Antibiograma completo (reporte de sensibilidad)

---

## 📊 MÉTRICAS DE PROGRESO (VERSIÓN FINAL - REALISTA)

| Fase | Total Items | Completados | Progreso | Estado |
|------|-------------|-------------|----------|--------|
| **FASE 0**: Datos + Hardware Reemplazo | 8 | 7 | 88% | ✅ Completo |
| **FASE 1**: Modelo de Datos SQLAlchemy | 4 | 4 | 100% | ✅ Completo |
| **FASE 2**: Motor AST Core | 4 | 4 | 100% | ✅ Completo | � En Progreso |
| **FASE 3**: GUI Wizard | 5 | 1 | 20% | � En Progreso |
| **FASE 4**: Integración GA + Mutaciones | 2 | 0 | 0% | 🔴 Pendiente |
| **FASE 5**: Testing | 3 | 0 | 0% | 🔴 Pendiente |
| **FASE 6**: Documentación | 3 | 0 | 0% | 🔴 Pendiente |
| **TOTAL** | **26** | **16** | **62%** | 🟡 EN PROGRESO |

---

# FASE 0: DATOS FUNDACIONALES + HARDWARE VIRTUAL (INNOVACIÓN)

## 📌 ITEM 0.0: Migración de Breakpoints (EUCAST + CLSI)
**Archivo**: `src/migrations/015_seed_breakpoints.sql`  
**Estado**: ✅ COMPLETADO (11-nov-2025, actualizado con CLSI completo)  
**Prioridad**: 🔥 CRÍTICA (Fundamento de interpretación S/R)  
**Estimación**: 1.5 horas  
**Tiempo real**: 2 horas

### ⚠️ CONTEXTO - DECISIÓN DE ESTÁNDAR
**Estándar primario:** EUCAST v15.0 (2025) - más reciente, simplificado (sin categoría "I")  
**Estándar fallback:** CLSI M07 (2023) - para validación cruzada y antibióticos sin EUCAST  
**Fuentes de datos:** 
- `docs/eucast_pseudomonas_aeruginosa_v15_2025.csv` (17 antibióticos EUCAST)
- `docs/pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv` (14 antibióticos CLSI)

**Razón**: Doble estándar permite validación cruzada y cobertura completa del panel de 15 antibióticos.

### Tareas
- [x] Crear script `scripts/generate_breakpoints_migration.py`
- [x] Crear tabla `breakpoints` con 9 columnas (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo, UNIQUE constraint)
- [x] Insertar 17 antibióticos desde EUCAST CSV
- [x] Insertar 14 antibióticos CLSI (13 del panel + Colistina exclusiva CLSI)
- [x] Incluir queries de validación en migración SQL
- [x] Total: 31 breakpoints generados (17 EUCAST + 14 CLSI)

### Resultados
- Archivo generado: `src/migrations/015_seed_breakpoints.sql` (actualizado 11-nov-2025)
- Cobertura: 15/15 antibióticos del panel tienen breakpoints
- Nota técnica: Colistina solo tiene CLSI (EUCAST no define para P. aeruginosa)
- Validación incluida: 4 queries SQL comentadas para verificar integridad
- Script reusable: `scripts/generate_breakpoints_migration.py` (274 líneas)

---

## 📌 ITEM 0.1: Migración de Matriz Gen × Clase (GENÉTICA PRECISA)
**Archivo**: `src/migrations/016_seed_gene_class_matrix.sql`  
**Estado**: ✅ COMPLETADO (10-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (Fundamento biológico de resistencia)  
**Estimación**: 1.5 horas  
**Tiempo real**: 1.5 horas

### ⚠️ CONTEXTO - FUNDAMENTO CIENTÍFICO AVANZADO
**Fuente:** `docs/matriz_genes_x_clases_MIC_multiplicadores_LONG_utf8_bom.csv` (11 genes × 9 clases = 99 combinaciones)

**Diferencia clave vs CSV anterior (mutaciones_pseudomonas_aeruginosa.csv):**
- ❌ CSV anterior: incremento MIC global (ej: gyrA → ×8 para todos los antibióticos)
- ✅ Matriz nueva: multiplicadores específicos por clase (ej: gyrA → ×8 fluoroquinolonas, ×1 carbapenem)

**Regla de acumulación:**
> Si una cepa tiene múltiples mutaciones, los efectos se **multiplican** para cada clase:
> ```
> MIC_final = MIC_base × mult_gen1 × mult_gen2 × ... × mult_genN
> ```
> Luego recortar al rango máximo del panel (ej: 64 µg/mL).

**Ejemplo real:**
- Bacteria con `oprD_loss` + `blaVIM` + `mexR_frameshift`
- Meropenem (carbapenemico):
  - MIC_base = 0.5 µg/mL
  - oprD_loss: ×8 → 4.0
  - blaVIM: ×16 → 64.0
  - mexR: ×1 (sin efecto en carbapenem) → 64.0
  - **MIC final**: 64 µg/mL (R)

**Clases de antibióticos (9):**
1. `carbapenemicos` (Meropenem, Imipenem, Doripenem)
2. `cef_3G_ceftazidima` (Ceftazidima)
3. `cef_4G_cefepime` (Cefepime)
4. `cef_inhibidor` (Ceftazidima/Avibactam, Ceftolozano/Tazobactam)
5. `monobactam_aztreonam` (Aztreonam)
6. `penicilina_inhibidor` (Piperacilina/Tazobactam)
7. `aminoglucosidos` (Amikacina, Tobramicina)
8. `fluoroquinolonas` (Ciprofloxacino, Levofloxacino)
9. `polimixinas` (Colistina)
10. `sideroforo_cefiderocol` (Cefiderocol)

**Genes documentados (11):**
- `gyrA_T83I`, `parC_S87L` (alteración blanco)
- `oprD_loss` (pérdida porina)
- `ampC_promoter_-32C_T`, `ampD_loss` (β-lactamasas)
- `mexR_frameshift`, `nalC_Q83K`, `mexZ_loss` (bombas eflujo)
- `ftsI_PBP3_insertion_YRIN` (alteración PBP)
- `blaVIM_or_blaIMP` (metalobetalactamasa)
- `pmrB_mut` (resistencia polimixinas)

### Tareas

- [x] Crear script `scripts/generate_gene_class_matrix_migration.py`
- [x] Crear tabla `gene_class_multipliers` (11 genes x 10 clases = 110 combinaciones)
- [x] Crear tabla `antibiotic_classes` (mapeo antibiótico → clase)
- [x] Insertar 110 filas gen×clase desde matriz CSV
- [x] Insertar 15 mapeos antibiótico→clase
- [x] Incluir queries de validación científica (gyrA×FQ=8, blaVIM×carbapenem=16, etc.)

### Resultados

- Archivo generado: `src/migrations/016_seed_gene_class_matrix.sql` (21001 caracteres, 411 líneas)
- Multiplicadores activos (>1.0): 30 de 110
- Multiplicadores neutros (=1.0): 80 de 110
- Multiplicador máximo: blaVIM_or_blaIMP × carbapenemicos = ×16.0
- Validación incluida: 5 queries SQL comentadas para verificar integridad científica
- Script reusable: `scripts/generate_gene_class_matrix_migration.py` (275 líneas)

---

## 📌 ITEM 0.2: Migración de Panel Layouts
**Archivo**: `src/migrations/017_seed_panel_layouts.sql`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (Define concentraciones del panel AST)  
**Estimación**: 1 hora  
**Tiempo real**: 1 hora

### ⚠️ CONTEXTO
**Fuente:** `docs/pseudomonas_aeruginosa_concentraciones_simuladas.csv` (13 antibióticos)  
**Serie log₂:** Cada antibiótico tiene 6-9 wells con concentraciones duplicadas  
**Total wells:** 91 test + 2 QC = 93 wells

### Tareas

- [x] Crear script `scripts/generate_panel_layouts_migration.py`
- [x] Crear tabla `panel_layouts` (panel_name, well_position, antibiotico, concentracion, tipo)
- [x] Generar series log2 automaticamente (0.25 → 0.5 → 1 → 2 → 4 → 8 → 16 → ...)
- [x] Asignar 91 wells test en posiciones A1-H10 (saltar H11, H12)
- [x] Insertar 2 controles QC: H11 (control_positivo), H12 (control_negativo)

### Resultados

- Archivo generado: `src/migrations/017_seed_panel_layouts.sql` (10305 caracteres, 136 líneas)
- Wells test: 91 (distribuidos en 13 antibioticos)
- Wells QC: 2 (H11 positivo, H12 negativo)
- Total: 93 wells
- Script reusable: `scripts/generate_panel_layouts_migration.py` (200 lineas)
- Optimizacion: Ordenamiento por numero de concentraciones (descendente) para maximizar uso del panel

---

## 📌 ITEM 0.3: Migración de Familias Antibióticas
**Archivo**: `src/migrations/018_update_antibioticos_familias.sql`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: ⚠️ MEDIA (Metadatos educativos)  
**Estimación**: 0.5 horas  
**Tiempo real**: 0.5 horas

### Tareas
- [x] Crear script `scripts/generate_antibioticos_familias_migration.py`
- [x] Agregar columnas familia y mecanismo_accion a tabla antibioticos
- [x] Generar 13 UPDATE statements desde CSV de familias
- [x] Incluir queries de validacion

### Resultados
- Archivo generado: `src/migrations/018_update_antibioticos_familias.sql` (3671 caracteres)
- 13 antibioticos actualizados con metadata educativa
- 9 familias unicas: Carbapenémico, Cefalosporinas (3ra/4ta gen), Aminoglucósido, Fluoroquinolona, Polimixina, β-lactámico+inhibidor, Cefalosporina+inhibidor, Cefalosporina sideróforo
- Script reusable: `scripts/generate_antibioticos_familias_migration.py` (127 lineas)

---

---

## 📌 ITEM 0.4: Generador de Perfiles Bacterianos (CIENTÍFICO)
**Archivo**: `src/core/bacteria_profile_generator.py`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (Reemplaza MALDI-TOF + preparación física)  
**Estimación**: 3 horas  
**Tiempo real**: 3 horas

### ⚠️ CONTEXTO IMPORTANTE
**En MicroScan real**: Técnico toma muestra física → MALDI-TOF identifica bacteria → Prepara inóculo  
**En nuestra app**: Usuario elige escenario clínico → Sistema genera bacteria in-silico

**Esto NO es una limitación, es una FEATURE educativa**:
- ✅ Usuario puede explorar diferentes escenarios sin esperar cultivos
- ✅ Sistema explica genotipo (MicroScan NO hace esto)
- ✅ **Mutaciones basadas en datos científicos reales** (CARD, NCBI AMR)

### Tareas

- [x] Constante global: `ORGANISM_NAME = "Pseudomonas aeruginosa"`
- [x] Dataclass `BacteriaProfile` para estructura de datos tipada
- [x] Funciones auxiliares: `get_wild_type_genotype()`, `get_baseline_mics()`
- [x] Método `generate_wild_type()` - Bacteria comunitaria sensible
- [x] Método `generate_from_history()` - Bacteria hospitalaria con mutaciones
- [x] Método `calculate_mic_with_multipliers()` - Regla multiplicativa
- [x] Método `get_multipliers_from_db()` - Consulta gene_class_multipliers
- [x] Método `format_profile_summary()` - Formato para GUI

### Resultados

- Archivo implementado: `src/core/bacteria_profile_generator.py` (387 líneas)
- Estructura: BacteriaProfile dataclass con type hints completos
- Genes documentados: 11 (gyrA, parC, oprD, mexR, ampC, ampD, ftsI, mexZ, nalC, blaVIM, pmrB)
- Antibióticos: 15 con MICs basales científicos
- Algoritmo: Regla multiplicativa MIC_final = MIC_base × ∏(multiplicadores)
- Integración: Consulta directa a gene_class_multipliers + antibiotic_classes
- Probabilidad de mutación: 70% por defecto (ajustable)
- Funcionalidad educativa: Genera perfiles determinísticos basados en exposición previa

### Método `generate_wild_type()` - Bacteria comunitaria sensible
  ```python
  def generate_wild_type():
      """Bacteria sensible estándar, sin exposición previa a antibióticos."""
      return {
          'organismo': 'Pseudomonas aeruginosa',
          'genes': {
              'gyrA': 'wild-type',
              'parC': 'wild-type',
              'oprD': 'functional',
              'mexR': 'functional',
              'ampC': 'basal',
              'ampD': 'functional',
              'ftsI': 'wild-type',
              'mexZ': 'functional',
              'nalC': 'wild-type'
          },
          'mics_base': {
              # Valores basales de bacteria sensible (antes de mutaciones)
              'Meropenem': 0.5,
              'Imipenem': 0.5,
              'Ciprofloxacino': 0.25,
              'Levofloxacino': 0.5,
              'Amikacina': 4.0,
              'Tobramicina': 1.0,
              'Cefepime': 2.0,
              'Ceftazidima': 2.0,
              # ... resto según breakpoints EUCAST
          }
      }
  ```

- [ ] Método `generate_from_history(antibioticos_previos)` - Bacteria hospitalaria **CON MUTACIONES CIENTÍFICAS**
  ```python
  from src.data.database import get_session
  from src.data.models import Mutation  # Nueva tabla (ITEM 0.1)
  import json
  
  def generate_from_history(antibioticos_previos: list[str]):
      """
      Genera bacteria con resistencias basadas en tratamientos previos.
      Consulta tabla `mutations` para aplicar cambios biológicamente plausibles.
      
      Args:
          antibioticos_previos: Lista de antibióticos (ej: ['Ciprofloxacino', 'Meropenem'])
      
      Returns:
          Dict con genotipo mutado y MICs calculados
      """
      session = get_session()
      
      # Punto de partida: bacteria wild-type
      profile = generate_wild_type()
      genes = profile['genes'].copy()
      mics = profile['mics_base'].copy()
      
      # Obtener todas las mutaciones de la tabla
      all_mutations = session.query(Mutation).all()
      
      # Filtrar mutaciones relevantes según antibióticos previos
      applied_mutations = []
      for mutation in all_mutations:
          antibioticos_afectados = json.loads(mutation.antibioticos_afectados)
          
          # Si algún antibiótico previo está en los afectados por esta mutación
          if any(ab in antibioticos_previos for ab in antibioticos_afectados):
              # Aplicar mutación al genotipo
              genes[mutation.gen] = mutation.tipo_mutacion
              
              # Incrementar MIC de antibióticos afectados
              for ab in antibioticos_afectados:
                  if ab in mics:
                      mics[ab] *= mutation.incremento_mic_factor
              
              applied_mutations.append({
                  'gen': mutation.gen,
                  'tipo': mutation.tipo_mutacion,
                  'mecanismo': mutation.mecanismo,
                  'fitness_cost': mutation.fitness_cost
              })
      
      return {
          'organismo': 'Pseudomonas aeruginosa',
          'genes': genes,
          'mics_base': mics,
          'mutaciones_aplicadas': applied_mutations,  # Para mostrar en GUI
          'escenario': 'hospitalizado'
      }
  ```

- [ ] Método `save_profile()` - Guardar perfil en tabla `bacteria_profiles`
  ```python
  def save_profile(profile_data, origen_muestra, antibioticos_previos=None):
      from src.data.models import BacteriaProfile
      
      new_profile = BacteriaProfile(
          organismo=profile_data['organismo'],
          escenario=profile_data.get('escenario', 'comunitario'),
          origen_muestra=origen_muestra,
          antibioticos_previos=json.dumps(antibioticos_previos or []),
          genotipo=json.dumps(profile_data['genes']),
          mics_base=json.dumps(profile_data['mics_base'])
      )
      session.add(new_profile)
      session.commit()
      return new_profile.id
  ```

### 💡 INTEGRACIÓN CON TABLA MUTATIONS
Este módulo ahora consulta la tabla `mutations` (ITEM 0.1) para:
- ✅ Aplicar mutaciones plausibles basadas en historial
- ✅ Calcular MICs usando factores científicos (×2, ×4, ×8, ×32)
- ✅ Registrar fitness cost para uso posterior en GA (FASE 4)

**NO ejecuta GA completo aquí** (eso es FASE 4). Solo aplica reglas determinísticas.

---

## 📌 ITEM 0.5: GUI - Página Escenario Clínico
**Archivo**: `src/gui/workflows/clinical_scenario_page.py`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA  
**Estimación**: 2 horas  
**Tiempo real**: 2 horas

### Tareas
- [x] Clase `ClinicalScenarioPage(QWizardPage)`
- [x] Dropdown: Origen de muestra (Hemocultivo/Esputo/Orina/Herida/Cateter)
- [x] RadioButton: Comunitario vs Hospitalizado
- [x] CheckList (solo si Hospitalizado): Antibioticos previos (10 antibioticos)
- [x] Boton: "Generar Bacteria" → Llama a `bacteria_profile_generator`
- [x] Label: Mostrar genotipo generado (educativo) usando `format_profile_summary()`

### Resultados
- Archivo implementado: `src/gui/workflows/clinical_scenario_page.py` (310 lineas)
- Componentes: QWizardPage con 4 secciones (origen, contexto, historial, resultado)
- Integracion: Llama directamente a `generate_wild_type()` y `generate_from_history()`
- Validacion: No permite avanzar hasta generar perfil bacteriano
- UX: Deshabilita seccion de antibioticos previos para contexto comunitario
- Senales: Emite `profile_generated` para integracion con wizard completo

### UI Mockup
```
┌─────────────────────────────────────────┐
│ Paso 1: Escenario Clínico              │
├─────────────────────────────────────────┤
│ Origen de muestra:                      │
│ [ Hemocultivo ▼ ]                       │
│                                         │
│ Contexto del paciente:                  │
│ ● Comunitario (bacteria estándar)      │
│ ○ Hospitalizado (tratado previamente)  │
│                                         │
│ [Si Hospitalizado:]                     │
│ Antibióticos usados antes:              │
│ ☐ Ciprofloxacino                        │
│ ☐ Meropenem                             │
│ ☐ Ceftazidima                           │
│                                         │
│ [ Generar Bacteria → ]                  │
│                                         │
│ Resultado:                              │
│ P. aeruginosa - Genotipo:               │
│ • gyrA: S83L (resistencia a Cipro)     │
│ • oprD: functional                      │
│                                         │
│ [Siguiente →]                           │
└─────────────────────────────────────────┘
```

---

---

## 📌 ITEM 0.6: Migración de Familias Antibióticas
**Archivo**: `src/migrations/018_update_antibioticos_familias.sql` (YA COMPLETADO EN ITEM 0.3)  
**Estado**: ✅ DUPLICADO - Ver ITEM 0.3  
**Prioridad**: ⚠️ MEDIA (Metadatos educativos)  
**Estimación**: 0.5 horas

### Nota
Este item es un duplicado del ITEM 0.3 que ya fue completado.
La migración 018_update_antibioticos_familias.sql ya existe y contiene:
- ALTER TABLE antibioticos ADD COLUMN familia, mecanismo_accion
- 13 UPDATE statements con familias y mecanismos

---

## 📌 ITEM 0.7: Tabla bacteria_profiles
**Archivo**: `src/migrations/019_create_bacteria_profiles.sql`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 0.5 horas  
**Tiempo real**: 0.5 horas

### Tareas
- [x] Crear tabla para almacenar perfiles generados
- [x] Definir columnas: organismo, escenario, origen_muestra, antibioticos_previos, genotipo, mics_calculated, mutaciones_aplicadas
- [x] Crear indices para optimizacion (escenario, created_at)
- [x] Incluir queries de validacion

### Resultados
- Archivo generado: `src/migrations/019_create_bacteria_profiles.sql` (61 lineas)
- Tabla: bacteria_profiles con 9 columnas
- Indices: 2 indices (escenario, created_at DESC)
- Campos JSON: antibioticos_previos, genotipo, mics_calculated, mutaciones_aplicadas
- Validacion: 4 queries SQL comentadas para testing

### 💡 NOTA
Esta tabla guarda el "punto de partida" bacteriano antes de AST. Útil para auditoría y análisis educativo.

---

**ESTIMACIÓN TOTAL FASE 0:** 9.5 horas (4 migraciones seed + 2 códigos + 1 GUI + 2 tablas nuevas)

---

### Tareas
- [ ] Crear tabla `bacteria_profiles`
  ```sql
  CREATE TABLE bacteria_profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      scenario_type VARCHAR(20) NOT NULL, -- 'wild_type' o 'hospital'
      antibiotic_history TEXT,            -- JSON: ["Ciprofloxacino", "Meropenem"]
      genotype TEXT NOT NULL,              -- JSON: {"gyrA": "S83L", ...}
      base_mics TEXT NOT NULL,             -- JSON: {"Meropenem": 16, ...}
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

---

# FASE 1: MODELO DE DATOS (MODELOS SQLAlchemy)

## 📌 ITEM 1.1: Modelos AST Core (5 clases SQLAlchemy)
**Archivo**: `src/data/models.py` (agregar a archivo existente)  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA  
**Estimación**: 1.5 horas  
**Tiempo real**: 1.5 horas

### Tareas
- [x] Agregar clase `Breakpoint` con método `interpret_mic()`
- [x] Agregar clase `GeneClassMultiplier` para matriz gen×clase
- [x] Agregar clase `AntibioticClass` para mapeo antibiótico→clase
- [x] Agregar clase `BacteriaProfile` para perfiles generados
- [x] Agregar clase `PanelLayout` para configuración de panel 96-wells
- [x] Verificar sintaxis y compilación

### Resultados
- Archivo actualizado: `src/data/models.py` (+120 líneas)
- 5 modelos nuevos agregados
- Total modelos en archivo: 16 (11 previos + 5 nuevos)
- Sintaxis validada: ✅ Sin errores
- Tablas correspondientes: Ya creadas en FASE 0 (migraciones 015-019)

### Modelos implementados

**1. Breakpoint** - Puntos de corte S/R
- Campos: antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo
- Método: `interpret_mic(mic_value)` retorna 'S' o 'R'
- Uso: Interpretación de resultados AST según EUCAST/CLSI

**2. GeneClassMultiplier** - Multiplicadores gen×clase
- Campos: gen, clase_antibiotica, multiplicador
- Uso: Cálculo de MICs mediante regla multiplicativa

**3. AntibioticClass** - Mapeo antibiótico→clase
- Campos: antibiotico, clase
- Uso: Determinar qué multiplicadores aplicar a cada antibiótico

**4. BacteriaProfile** - Perfiles bacterianos generados
- Campos: organismo, escenario, origen_muestra, antibioticos_previos, genotipo, mics_calculated, mutaciones_aplicadas, created_at
- Uso: Almacenar estado inicial de bacteria antes de AST

**5. PanelLayout** - Layout de panel 96-wells
- Campos: panel_name, well_position, antibiotico, concentracion, tipo
- Uso: Definir distribución de antibióticos y concentraciones en placa

---

**ESTIMACIÓN TOTAL FASE 1:** 1.5 horas (5 modelos SQLAlchemy)

**NOTA**: Las tablas SQL correspondientes ya fueron creadas en FASE 0 (migraciones 015-019).

---

### ⚠️ RESTRICCIÓN IMPORTANTE
**NO crear tabla `organisms`** - El organismo es fijo: *Pseudomonas aeruginosa*  
**Razón**: Simplificar simulación, evitar complejidad de identificación bacteriana  
**Implicación**: Los breakpoints y runs asumirán P. aeruginosa por defecto

### Tareas
- [x] ~~Crear tabla `organisms`~~ **OMITIDO** (organismo fijo en código)
  - Hardcoded: `ORGANISM_NAME = "Pseudomonas aeruginosa"`
  - Hardcoded: `ORGANISM_GRAM = "negativo"`
  
- [ ] Crear tabla `panel_layouts` (configuración de paneles)
  - Campos: id, nombre, tipo_bacteria, descripcion
  
- [ ] Crear tabla `panel_concentrations` (concentraciones por panel)
  - Campos: id, panel_layout_id, antibiotico_id, concentracion_ug_ml, posicion_pocillo
  - Constraint: UNIQUE(panel_layout_id, posicion_pocillo)
  
- [ ] Crear tabla `ast_runs` (ejecuciones de AST)
  - Campos: id, panel_layout_id, fecha, temperatura, inoculo_mcfarland, duracion_horas, qc_status, notas
  - **SIN organism_id** (siempre P. aeruginosa)
  - Constraint: temperatura típica 35-37°C, inóculo típico 0.5 McFarland
  
- [ ] Crear tabla `ast_wells` (pocillos individuales)
  - Campos: id, run_id, antibiotico_id, concentracion_ug_ml, posicion_pocillo, es_control_positivo, es_control_negativo
  
- [ ] Crear tabla `well_readings` (series temporales)
  - Campos: id, well_id, tiempo_minutos, od_600, turbidez, crecimiento_detectado
  
- [ ] Crear tabla `ast_mic_results` (resultados MIC)
  - Campos: id, run_id, antibiotico_id, mic_ug_ml, mic_operador, metodo, algoritmo_usado, confianza
  
- [ ] Crear tabla `breakpoints` (puntos de corte oficiales)
  - Campos: id, antibiotico_id, guideline, version, breakpoint_s, breakpoint_r, notas, fecha_vigencia
  - **SIN organism_id** (siempre P. aeruginosa)
  - Ejemplo: Meropenem CLSI-2025: S≤2, R≥8
  
- [ ] Crear tabla `ast_interpretations` (interpretación S/I/R)
  - Campos: id, mic_result_id, breakpoint_id, categoria, guideline, version, fecha_interpretacion
  
- [ ] Crear tabla `ast_qc_checks` (control de calidad)
  - Campos: id, run_id, tipo_control, resultado, mensaje, timestamp

### Consideraciones Técnicas
- **Organismo fijo**: *Pseudomonas aeruginosa* (hardcoded en código Python)
- Diluciones dobles: 0.03, 0.06, 0.12, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64 µg/mL
- Placa 96 pocillos: 8 filas (A-H) × 12 columnas (1-12)
- Series temporales: lecturas cada 60 min (0, 60, 120, 180... hasta 1080 min = 18h)
- OD600 rango: 0.0 (claro) a 4.0+ (muy turbio)
- **Breakpoints**: Solo para P. aeruginosa (CLSI M100 Table 2B)

### SQL Template
```sql
-- ESQUEMA SIMPLIFICADO (sin tabla organisms)
CREATE TABLE panel_layouts (...);
CREATE TABLE ast_runs (
  id INTEGER PRIMARY KEY,
  -- NO organism_id (siempre P. aeruginosa)
  panel_layout_id INTEGER,
  ...
);
CREATE TABLE breakpoints (
  id INTEGER PRIMARY KEY,
  -- NO organism_id (siempre P. aeruginosa)
  antibiotico_id INTEGER,
  ...
);
-- ... etc
```

### 💡 NOTA PARA EL AGENTE (YO)
En el código Python (`ast_simulator.py`), definir constante:
```python
# Organismo fijo del simulador
ORGANISM_NAME = "Pseudomonas aeruginosa"
ORGANISM_GRAM = "negativo"
```

---

## 📌 ITEM 1.2: Migración SQL - Breakpoints CLSI/EUCAST
**Archivo**: `src/migrations/015_seed_breakpoints.sql`  
**Estado**: ✅ COMPLETADO EN FASE 0 (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1-2 horas  
**Tiempo real**: 2 horas (ITEM 0.0)

### Nota
Este item fue completado como **ITEM 0.0** en FASE 0.
- Migración generada: `015_seed_breakpoints.sql`
- 31 breakpoints (17 EUCAST + 14 CLSI)
- Cobertura: 15/15 antibióticos del panel

**Ver ITEM 0.0 para detalles completos.**

### ⚠️ ACLARACIÓN IMPORTANTE
**Breakpoints NO son visibles para el usuario final en MVP**.

El usuario solo ve:
- ✅ MIC calculado (ej: 2.0 µg/mL)
- ✅ Interpretación S/I/R (ej: 🟢 Sensible)
- ✅ Guideline usado (ej: CLSI)

Los breakpoints son **datos internos** que el sistema usa para calcular S/I/R.
Usuario NO necesita saber que "breakpoint_s = 2.0" para Meropenem.

### ⚠️ RESTRICCIÓN IMPORTANTE
**SOLO breakpoints para *Pseudomonas aeruginosa***  
**Fuente principal**: CLSI M100-2025 **Table 2B** (Non-Enterobacterales)

### Tareas
- [x] ~~Insertar organismos base~~ **OMITIDO** (solo P. aeruginosa, hardcoded)
  
- [ ] Cargar breakpoints CLSI M100-2025 **SOLO P. aeruginosa** (mínimo 15 combinaciones)
  - ✅ P. aeruginosa + Meropenem: S≤2, R≥8
  - ✅ P. aeruginosa + Imipenem: S≤2, R≥8
  - ✅ P. aeruginosa + Ciprofloxacino: S≤1, R≥4
  - ✅ P. aeruginosa + Levofloxacino: S≤2, R≥8
  - ✅ P. aeruginosa + Gentamicina: S≤4, R≥16
  - ✅ P. aeruginosa + Amikacina: S≤16, R≥64
  - ✅ P. aeruginosa + Tobramicina: S≤4, R≥16
  - ✅ P. aeruginosa + Ceftazidima: S≤8, R≥32
  - ✅ P. aeruginosa + Cefepima: S≤8, R≥32
  - ✅ P. aeruginosa + Piperacilina-Tazobactam: S≤16, R≥128
  - ✅ P. aeruginosa + Aztreonam: S≤8, R≥32
  - ✅ P. aeruginosa + Colistina: S≤2, R≥4
  - ✅ P. aeruginosa + Polimixina B: S≤2, R≥4
  - ✅ P. aeruginosa + Ceftolozano-Tazobactam: S≤4, R≥16
  - ✅ P. aeruginosa + Ceftazidima-Avibactam: S≤8, R≥32
  
- [ ] Cargar breakpoints EUCAST v15.0 **SOLO P. aeruginosa** (mínimo 8 combinaciones)
  - Priorizar donde difieren de CLSI (ejemplo: Colistina EUCAST S≤2, CLSI S≤2)

### Fuentes de Datos
- **CLSI M100-2025**: **Table 2B** (Pseudomonas aeruginosa y otros non-fermenters)
- **EUCAST v15.0**: Clinical Breakpoints - Pseudomonas spp.
- **Archivo CSV existente**: `docs/pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv` (¡YA EXISTE!)
- **Disclaimer**: Uso educativo únicamente, verificar versiones oficiales vigentes

### 💡 NOTA PARA EL AGENTE (YO)
**¡IMPORTANTE!** Ya existe archivo CSV con breakpoints de P. aeruginosa:
`docs/pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv`

**Acción**: Revisar ese CSV primero antes de crear el SQL. Puedo reutilizar esos datos.

### Template SQL
```sql
-- SIMPLIFICADO: Sin tabla organisms
INSERT INTO breakpoints (antibiotico_id, guideline, version, breakpoint_s, breakpoint_r, notas) VALUES
  ((SELECT id FROM antibioticos WHERE nombre='Meropenem'),
   'CLSI', 'M100-2025', 2.0, 8.0, 'Pseudomonas aeruginosa - Table 2B'),
  ((SELECT id FROM antibioticos WHERE nombre='Ciprofloxacino'),
   'CLSI', 'M100-2025', 1.0, 4.0, 'Pseudomonas aeruginosa - Table 2B'),
  ((SELECT id FROM antibioticos WHERE nombre='Gentamicina'),
   'CLSI', 'M100-2025', 4.0, 16.0, 'Pseudomonas aeruginosa - Table 2B'),
  -- ... resto de breakpoints solo para P. aeruginosa
  
  -- EUCAST (cuando difiere)
  ((SELECT id FROM antibioticos WHERE nombre='Colistina'),
   'EUCAST', 'v15.0', 2.0, 2.0, 'Pseudomonas aeruginosa - No intermediate');
```

---

## 📌 ITEM 1.3: Migración SQL - Paneles Predefinidos
**Archivo**: `src/migrations/017_seed_panel_layouts.sql`  
**Estado**: ✅ COMPLETADO EN FASE 0 (11-nov-2025)  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 1 hora  
**Tiempo real**: 1 hora (ITEM 0.2)

### Nota
Este item fue completado como **ITEM 0.2** en FASE 0.
- Migración generada: `017_seed_panel_layouts.sql`
- 93 wells (91 test + 2 QC)
- Panel: Pseudomonas Standard Panel

**Ver ITEM 0.2 para detalles completos.**

### ⚠️ RESTRICCIÓN IMPORTANTE
**Panel único**: "Pseudomonas Standard Panel"  
**Tipo**: gram_negativo (fijo, solo P. aeruginosa)

### Tareas
- [x] ~~Crear panel "Gram Negative Standard"~~ → **Renombrar a "Pseudomonas Standard Panel"**
  - Tipo: gram_negativo (siempre)
  - Antibióticos específicos para P. aeruginosa:
    - ✅ Carbapenems: Meropenem, Imipenem
    - ✅ Fluoroquinolonas: Ciprofloxacino, Levofloxacino
    - ✅ Aminoglicósidos: Gentamicina, Amikacina, Tobramicina
    - ✅ Cefalosporinas: Ceftazidima, Cefepima
    - ✅ Beta-lactam/inhibidor: Piperacilina-Tazobactam
    - ✅ Monobactam: Aztreonam
    - ✅ Polimixinas: Colistina
  - 8-12 concentraciones por antibiótico (diluciones dobles)
  
- [x] ~~Crear panel "Gram Positive Standard"~~ **OMITIDO** (no aplica a P. aeruginosa)
  
- [ ] Configurar posiciones de pocillos (layout físico 96)
  - Filas A-D: Antibiótico 1 (concentraciones crecientes)
  - Filas E-H: Antibiótico 2
  - Columnas 1-2: Controles +/−

### Consideraciones
- Dejar posiciones para controles positivo/negativo (pocillos H11, H12)
- Cubrir breakpoints ±2 diluciones para cada antibiótico
- Ejemplo Meropenem: Si breakpoint S=2, cubrir 0.5, 1, 2, 4, 8, 16 µg/mL
- **Total antibióticos**: ~12 (todos específicos para P. aeruginosa)
- **Total pocillos usados**: ~85 de 96 (11 pocillos de reserva)

### 💡 NOTA PARA EL AGENTE (YO)
Verificar que todos los antibióticos en el panel existan en tabla `antibioticos` (migración 002_seed_data.sql).
Si falta alguno (ej: Ceftolozano-Tazobactam), agregarlo primero.

---

## 📌 ITEM 1.4: Actualizar Modelos SQLAlchemy
**Archivo**: `src/data/models.py`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1 hora  
**Tiempo real**: 0.5 horas (parte de ITEM 1.1)

### Nota
Este item fue completado como parte de **ITEM 1.1**.
- 5 modelos agregados: Breakpoint, GeneClassMultiplier, AntibioticClass, BacteriaProfile, PanelLayout
- Sin clase Organism (organismo fijo: P. aeruginosa)

**Ver ITEM 1.1 para detalles completos.**

### Tareas
- [x] ~~Crear clase `Organism`~~ **OMITIDO** (organismo fijo)
- [ ] Crear clase `PanelLayout`
- [ ] Crear clase `PanelConcentration`
- [ ] Crear clase `ASTRun` (sin foreign key organism_id)
- [ ] Crear clase `ASTWell`
- [ ] Crear clase `WellReading`
- [ ] Crear clase `ASTMICResult`
- [ ] Crear clase `Breakpoint` (sin foreign key organism_id)
- [ ] Crear clase `ASTInterpretation`
- [ ] Crear clase `ASTQCCheck`
- [ ] Configurar relaciones (ForeignKey, relationship)

### Template Python
```python
# Constante global (NO tabla)
ORGANISM_NAME = "Pseudomonas aeruginosa"
ORGANISM_GRAM = "negativo"

class ASTRun(Base):
    __tablename__ = "ast_runs"
    id = Column(Integer, primary_key=True)
    # NO organism_id (siempre P. aeruginosa)
    panel_layout_id = Column(Integer, ForeignKey("panel_layouts.id"))
    fecha = Column(DateTime, default=datetime.utcnow)
    temperatura = Column(Float, default=37.0)
    inoculo_mcfarland = Column(Float, default=0.5)
    # ...
    
class Breakpoint(Base):
    __tablename__ = "breakpoints"
    id = Column(Integer, primary_key=True)
    # NO organism_id (siempre P. aeruginosa)
    antibiotico_id = Column(Integer, ForeignKey("antibioticos.id"))
    guideline = Column(String(20))  # 'CLSI' o 'EUCAST'
    # ...
```

### 💡 NOTA PARA EL AGENTE (YO)
En todo el código, cuando necesite el nombre del organismo, usar la constante:
```python
from src.data.models import ORGANISM_NAME
print(f"Organismo: {ORGANISM_NAME}")  # "Pseudomonas aeruginosa"
```

---

# FASE 2: LÓGICA DE NEGOCIO (CORE)

## 📌 ITEM 2.1: Módulo ASTSimulator
**Archivo**: `src/core/ast_simulator.py`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 4-6 horas  
**Tiempo real**: 4 horas

### Tareas
- [x] Definir constantes globales (ORGANISM_NAME, DEFAULT_TEMPERATURE, etc.)
- [x] Clase `ASTSimulator.__init__()` sin organism_id
- [x] Método `simulate_incubation()` - Simular 18h de incubación
- [x] Método `_simulate_test_well()` - Curva logística por pocillo
- [x] Método `_simulate_control_well()` - Controles QC
- [x] Método `calculate_mics()` - Calcular MICs de todos los antibióticos
- [x] Método `_calculate_mic_by_threshold()` - Algoritmo umbral OD
- [x] Método `_calculate_mic_by_interpolation()` - Interpolación lineal
- [x] Método `_interpret_mic()` - Mapeo MIC → S/R con breakpoints
- [x] Método `apply_qc_checks()` - Validar controles +/−
- [x] Método `get_report()` - Generar reporte completo JSON

### Resultados
- Archivo creado: `src/core/ast_simulator.py` (540 líneas)
- Dataclasses: WellReading, WellData, MICResult
- Algoritmos: Umbral OD (0.3) e interpolación lineal
- Curva de crecimiento: Modelo logístico con parámetros ajustados a P. aeruginosa
- Integración: Usa BacteriaProfile, PanelLayout, Breakpoint de BD
- QC: Validación automática de controles positivo/negativo

### Características Implementadas

**1. Simulación de Incubación**
- Lecturas cada 60 min (0-1080 min = 18h)
- Curva logística ajustada según MIC vs concentración
- Crecimiento diferencial: completo si [AB] < MIC, inhibido si [AB] >= MIC

**2. Cálculo de MIC**
- Método umbral: Primera concentración con OD < 0.3
- Método interpolación: Valor exacto entre dos diluciones
- Operadores: =, >=, ≈

**3. Interpretación S/R**
- Usa breakpoints EUCAST (primario)
- Fallback a CLSI si EUCAST no disponible
- Método `Breakpoint.interpret_mic()` del modelo

**4. Control de Calidad**
- Control positivo: OD > 1.0 (crecimiento esperado)
- Control negativo: OD < 0.1 (esterilidad)
- QC global: Ambos controles deben pasar

**5. Reporte JSON**
- Metadata: organismo, temperatura, inóculo, duración
- QC: Estado de controles
- MICs: Valor, operador, interpretación, confianza
- Resumen: Total S/R, QC status

---

## 📌 ITEM 2.2: Módulo Growth Models
**Archivo**: `src/core/growth_models.py`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 2-3 horas  
**Tiempo real**: 1.5 horas

### Tareas
- [x] Función `logistic_growth(t, od_max, k, t_mid, od_initial)`
- [x] Función `calculate_od_max_with_antibiotic(base_od_max, concentration, mic_real)`
- [x] Función `add_measurement_noise(od_value, noise_level=0.05)`
- [x] Función `classify_turbidity(od_value)` → 'claro', 'ligero', 'moderado', 'turbio'
- [x] Función EXTRA: `calculate_growth_parameters(mic_value, concentration, ...)` (helper)
- [x] Función EXTRA: `simulate_well_growth_curve(...)` (integración completa)

### Modelo Matemático
```python
def logistic_growth(t, od_max, k, t_mid, od_initial=0.05):
    """
    Curva logística (Verhulst):
    OD(t) = od_initial + (od_max - od_initial) / (1 + exp(-k*(t - t_mid)))
    """
    return od_initial + (od_max - od_initial) / (1 + np.exp(-k * (t - t_mid)))

def calculate_od_max_with_antibiotic(base_od_max, concentration, mic_real):
    """
    Inhibición por antibiótico (Hill equation):
    ODmax_inhibido = ODmax_base / (1 + (C/MIC)^n)
    
    Donde n = 4 (coeficiente de Hill)
    """
    hill_coefficient = 4
    survival = 1 / (1 + (concentration / mic_real) ** hill_coefficient)
    return base_od_max * survival
```

### Resultados ITEM 2.2
**Archivo creado**: `src/core/growth_models.py` (274 líneas)

**Funciones implementadas** (6 totales):
1. **`logistic_growth(t, od_max, k, t_mid, od_initial)`**:
   - Ecuación de Verhulst implementada con protección contra overflow
   - Límites en exponente: [-100, 100]
   - Documentación con ejemplo ejecutable

2. **`calculate_od_max_with_antibiotic(base_od_max, concentration, mic_real, hill_coefficient=4.0)`**:
   - Ecuación de Hill con coeficiente n=4 (por defecto)
   - Validación de MIC > 0
   - Manejo de concentración ≤ 0 (retorna od_max sin inhibición)

3. **`add_measurement_noise(od_value, noise_level=0.05)`**:
   - Ruido gaussiano con desviación estándar relativa
   - Nivel típico: 2-10% (0.02-0.10)
   - Valores OD negativos corregidos a 0.0

4. **`classify_turbidity(od_value)`**:
   - Retorna tupla: `(categoría, descripción)`
   - 5 categorías: claro, ligero, moderado, turbio, muy_turbio
   - Rangos de OD: <0.1, 0.1-0.3, 0.3-1.0, 1.0-2.0, ≥2.0

5. **`calculate_growth_parameters(mic_value, concentration, ...)`** (EXTRA):
   - Calcula parámetros ajustados (od_max, k, t_mid)
   - Lógica: C < MIC (normal), C ≈ MIC (reducido), C >> MIC (mínimo)
   - Retarda t_mid y reduce k para concentraciones altas

6. **`simulate_well_growth_curve(mic_value, concentration, time_points, ...)`** (EXTRA):
   - Función de alto nivel que integra todos los modelos
   - Genera serie temporal completa con ruido opcional
   - Usa `calculate_growth_parameters()` + `logistic_growth()` + `add_measurement_noise()`

**Validaciones**:
- ✅ Todas las funciones con type hints
- ✅ Docstrings con ejemplos ejecutables
- ✅ Manejo de casos edge (MIC≤0, concentración≤0, OD negativo)
- ✅ Protección contra overflow matemático (exp)
- ✅ Imports mínimos: math, random, typing.Tuple

**Integración con ASTSimulator**:
- `logistic_growth()` → llamada desde `_simulate_test_well()`
- `calculate_od_max_with_antibiotic()` → cálculo de od_max inhibido
- `add_measurement_noise()` → ruido opcional en lecturas
- `classify_turbidity()` → interpretación visual de OD



---

## 📌 ITEM 2.3: Módulo Breakpoint Service
**Archivo**: `src/core/breakpoint_service.py`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1.5 horas (SIMPLIFICADO)  
**Tiempo real**: 2 horas

### Tareas
- [x] Método `get_breakpoint(antibiotico_id, guideline='EUCAST', version=None)`
  - **SIN parámetro organism_id** (siempre P. aeruginosa)
  - Query directo a tabla `breakpoints` filtrado solo por antibiotico_id
  - Fallback automático: EUCAST → CLSI si no encuentra
  
- [x] Método `get_breakpoint_by_name(antibiotico_nombre, guideline='EUCAST')`
- [x] Método `interpret_mic(mic_value, mic_operator, breakpoint_s, breakpoint_r)`
- [x] Método `interpret_with_breakpoint(mic_value, mic_operator, antibiotico_id, guideline)`
- [x] Método `check_breakpoint_coverage(panel_layout_id, antibiotico_id)`
- [x] Método `get_all_breakpoints_for_panel(antibiotico_ids, guideline)`
- [x] Cacheo de breakpoints frecuentes con `_breakpoint_cache`
- [x] Métodos utilitarios: `clear_cache()`, `get_cache_stats()`

### 💡 NOTA PARA EL AGENTE (YO)
Simplificar query SQL:
```python
# ANTES (genérico):
breakpoint = session.query(Breakpoint).filter(
    Breakpoint.organism_id == organism_id,  # ❌ Ya no existe
    Breakpoint.antibiotico_id == antibiotico_id
).first()

# AHORA (simplificado):
breakpoint = session.query(Breakpoint).filter(
    Breakpoint.antibiotico_id == antibiotico_id,
    Breakpoint.guideline == guideline
).first()  # Asume P. aeruginosa implícitamente
```

### Lógica de Interpretación S/I/R
```python
def interpret_mic(mic_value, mic_operator, breakpoint_s, breakpoint_r):
    """
    Reglas:
    - MIC ≤ breakpoint_s → S (Sensible)
    - breakpoint_s < MIC < breakpoint_r → I (Intermedio)
    - MIC ≥ breakpoint_r → R (Resistente)
    
    Casos especiales:
    - MIC_operator = '<=' → MIC ≤ valor, probablemente S
    - MIC_operator = '>=' → MIC ≥ valor, probablemente R
    """
    if mic_operator == '<=':
        return 'S' if mic_value <= breakpoint_s else 'I'
    elif mic_operator == '>=':
        return 'R' if mic_value >= breakpoint_r else 'I'
    else:  # '='
        if mic_value <= breakpoint_s:
            return 'S'
        elif mic_value >= breakpoint_r:
            return 'R'
        else:
            return 'I'
```

### Resultados ITEM 2.3
**Archivo creado**: `src/core/breakpoint_service.py` (398 líneas)

**Clase principal**: `BreakpointService`

**Métodos implementados** (9 totales):

1. **`__init__(use_cache=True)`**:
   - Inicializa sesión SQLAlchemy
   - Activa cache de breakpoints en memoria

2. **`get_breakpoint(antibiotico_id, guideline='EUCAST', version=None)`**:
   - Query simplificado sin organism_id
   - Fallback automático: EUCAST → CLSI
   - Orden por versión descendente (más reciente primero)
   - Uso de cache para optimización

3. **`get_breakpoint_by_name(antibiotico_nombre, guideline='EUCAST')`**:
   - Wrapper para buscar por nombre de antibiótico
   - Consulta tabla `antibioticos` primero

4. **`interpret_mic(mic_value, mic_operator, breakpoint_s, breakpoint_r)`**:
   - Lógica S/I/R completa
   - Manejo de operadores: '=', '<=', '>='
   - Normalización de operadores (≤ → <=, ≥ → >=)
   - Interpretación conservadora en casos ambiguos

5. **`interpret_with_breakpoint(mic_value, mic_operator, antibiotico_id, guideline)`**:
   - Función de conveniencia: combina get_breakpoint + interpret_mic
   - Retorna tupla: (interpretación, breakpoint_usado)
   - Retorna 'UNKNOWN' si no encuentra breakpoint

6. **`check_breakpoint_coverage(panel_layout_id, antibiotico_id, guideline)`**:
   - Verifica si panel cubre breakpoints S y R
   - Criterio: ±1 dilución (factor 2) alrededor de breakpoint
   - Retorna dict con covers_s, covers_r, missing_concentrations, panel_concentrations

7. **`get_all_breakpoints_for_panel(antibiotico_ids, guideline)`**:
   - Carga múltiples breakpoints de una vez
   - Útil para inicialización de simulación
   - Retorna dict {antibiotico_id: Breakpoint}

8. **`clear_cache()`**:
   - Limpia cache global `_breakpoint_cache`
   - Útil si se actualizan breakpoints en BD

9. **`get_cache_stats()`**:
   - Retorna estadísticas: cached_entries, cache_enabled

**Características**:
- ✅ Cache global en memoria para consultas frecuentes
- ✅ Fallback automático EUCAST → CLSI
- ✅ Sin organism_id (P. aeruginosa implícito)
- ✅ Type hints completos
- ✅ Docstrings con ejemplos ejecutables
- ✅ Manejo robusto de operadores MIC

**Integración con ASTSimulator**:
- `get_breakpoint()` → llamada desde `_interpret_mic()` del simulador
- `interpret_with_breakpoint()` → interpretación directa de MICs
- `check_breakpoint_coverage()` → validación de diseño de panel



---

## 📌 ITEM 2.4: Módulo QC Validator
**Archivo**: `src/core/qc_validator.py`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 2 horas  
**Tiempo real**: 2.5 horas

### Tareas
- [x] Dataclass `QCResult` - Resultado de validación individual
- [x] Dataclass `CoherenceIssue` - Problema de coherencia detectado
- [x] Método `validate_positive_control(od_value, well_position)` - OD > 1.0
- [x] Método `validate_negative_control(od_value, well_position)` - OD < 0.1
- [x] Método `validate_coherence(mic_results)` - Antibióticos relacionados
- [x] Método `generate_qc_report(positive_od, negative_od, mic_results)` - Reporte completo
- [x] Método `reset()` - Limpia validaciones previas
- [x] Métodos auxiliares: `_check_cross_resistance()`, `_check_hierarchical()`, `_check_similar_activity()`

### Reglas de Coherencia
```python
COHERENCE_RULES = {
    'carbapenems': ['Imipenem', 'Meropenem', 'Ertapenem'],
    # Si Imipenem R → Meropenem probablemente R (mismo mecanismo)
    
    'fluoroquinolonas': ['Ciprofloxacino', 'Levofloxacino'],
    # Resistencia cruzada común
}
```

### Resultados ITEM 2.4
**Archivo creado**: `src/core/qc_validator.py` (480 líneas)

**Dataclasses** (2):
1. **`QCResult`**: Resultado de validación individual (check_type, passed, value, expected_range, message, severity)
2. **`CoherenceIssue`**: Problema de coherencia (family, antibiotics, issue, expected, actual, severity)

**Constantes globales**:
- **`COHERENCE_RULES`**: 4 familias (carbapenems, fluoroquinolonas, aminoglucosidos, cefalosporinas_antipseudomonas)
- **`QC_THRESHOLDS`**: Umbrales para controles (positive ≥1.0, negative ≤0.1, test_max ≤3.0)

**Clase principal**: `QCValidator`

**Métodos públicos** (6):

1. **`validate_positive_control(od_value, well_position='H11')`**:
   - Valida OD ≥ 1.0 (crecimiento robusto)
   - Severidades: PASS, WARNING (≥0.8), FAIL (<0.8)
   - Retorna `QCResult`

2. **`validate_negative_control(od_value, well_position='H12')`**:
   - Valida OD ≤ 0.1 (sin contaminación)
   - Severidades: PASS, WARNING (≤0.15), FAIL (>0.15)
   - Retorna `QCResult`

3. **`validate_coherence(mic_results)`**:
   - Valida 3 tipos de reglas: cross_resistance, hierarchical, similar
   - Detecta: resistencia cruzada inconsistente, jerarquía invertida, diferencias excesivas
   - Retorna `List[CoherenceIssue]`

4. **`generate_qc_report(positive_od, negative_od, mic_results=None)`**:
   - Genera reporte completo con timestamp
   - Determina overall_status: PASS / WARNING / FAIL
   - Retorna dict estructurado con controls, coherence, summary

5. **`reset()`**:
   - Limpia qc_results y coherence_issues

**Métodos privados** (3):

6. **`_check_cross_resistance(family, results, tolerance, description)`**:
   - Si uno es R, esperamos I/R en los demás (no S)
   - Genera WARNING si hay resistente + sensible simultáneo

7. **`_check_hierarchical(family, results, description)`**:
   - Verifica Amikacina MIC ≤ Gentamicina MIC
   - Genera WARNING si jerarquía invertida (Amikacina >2x peor)

8. **`_check_similar_activity(family, results, tolerance, description)`**:
   - Compara MICs por pares usando log2
   - Genera WARNING si diferencia > tolerance diluciones

**Características técnicas**:
- ✅ Basado en CLSI M07 guidelines
- ✅ 4 familias de antibióticos con reglas específicas
- ✅ Severidades: PASS (verde), WARNING (amarillo), FAIL (rojo)
- ✅ Type hints completos con dataclasses
- ✅ Docstrings con ejemplos ejecutables
- ✅ Validación borderline (80-100% para positivo, 100-150% para negativo)

**Integración con ASTSimulator**:
- `apply_qc_checks()` del simulador → usará `generate_qc_report()`
- Validación automática post-simulación
- Alertas en reporte final si QC FAIL



---

# FASE 3: INTERFAZ DE USUARIO (GUI)

## 📌 ITEM 3.1: Widget AST Panel
**Archivo**: `src/gui/widgets/ast_panel_widget.py`  
**Estado**: ✅ COMPLETADO (11-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1.5-2 horas (SIMPLIFICADO)  
**Tiempo real**: 2 horas

### Tareas
- [x] ~~ComboBox para selección de organismo~~ **OMITIDO** (siempre P. aeruginosa)
  - Mostrar label fijo: "Organismo: *Pseudomonas aeruginosa*"
  
- [x] ComboBox para selección de panel
  - Cargar desde BD (tabla `panel_layouts`)
  - Por defecto: "Pseudomonas Standard Panel"
  
- [x] SpinBox para inóculo (McFarland)
  - Rango: 0.3 - 0.7 (típico 0.5)
  
- [x] SpinBox para temperatura
  - Rango: 35-37°C (fijo en mayoría de casos)
  
- [x] Label fijo para duración
  - Fijo: 18.0 horas (estándar AST)
  
- [x] Botón "Ejecutar AST" con estilo verde
- [x] ProgressBar durante simulación (0-100%)
- [x] Signal `ast_completed(report)` y `ast_failed(error_msg)`
- [x] Clase `ASTWorker(QThread)` para ejecución asíncrona
- [x] Método `set_bacteria_profile(bacteria_profile_id)`

### UI Layout SIMPLIFICADO
```
┌─────────────────────────────────┐
│ Configuración AST               │
├─────────────────────────────────┤
│ Organismo: Pseudomonas aerugin… │  ← Label fijo (no editable)
│ Panel: [Pseudomonas Std ▼]      │
│ Inóculo (McF): [0.5]            │
│ Temperatura (°C): [37.0]        │
│ Duración (h): [18.0] (fijo)     │
│                                 │
│ [   Ejecutar AST   ]            │
│ [████████░░] 80%                │
└─────────────────────────────────┘
```

### Resultados ITEM 3.1
**Archivo creado**: `src/gui/widgets/ast_panel_widget.py` (447 líneas)

**Clases implementadas** (2):

1. **`ASTWorker(QThread)`**: Thread para simulación asíncrona
   - **Signals**: progress(int), finished(dict), error(str)
   - **Pasos**: Simulación (40%) → Cálculo MICs (30%) → QC (20%) → Reporte (10%)
   - **run()**: Ejecuta ASTSimulator completo sin bloquear UI

2. **`ASTPanelWidget(QWidget)`**: Widget principal
   - **Signals**: ast_completed(dict), ast_failed(str)
   - **Métodos públicos**:
     - `set_bacteria_profile(bacteria_profile_id)`: Establece perfil para simulación
   - **Métodos privados**:
     - `_init_ui()`: Construye interfaz con QFormLayout
     - `_load_panels()`: Carga paneles desde BD (PanelLayout.panel_name distinct)
     - `_on_run_clicked()`: Validación y confirmación pre-simulación
     - `_start_simulation(panel_layout_id)`: Inicializa worker thread
     - `_on_progress(value)`: Actualiza barra y mensajes (incubación/MICs/QC/reporte)
     - `_on_finished(report)`: Rehabilita UI, emite signal, muestra resumen
     - `_on_error(error_msg)`: Maneja errores con QMessageBox.critical

**Componentes UI** (10):
1. **QLabel**: Organismo fijo (P. aeruginosa en negrita)
2. **QComboBox**: Selector de panel (carga desde BD)
3. **QDoubleSpinBox**: Inóculo (0.3-0.7 McF, step 0.1)
4. **QDoubleSpinBox**: Temperatura (35-37°C, step 0.5)
5. **QLabel**: Duración fija (18.0h estándar)
6. **QPushButton**: Ejecutar AST (verde, bold, con hover)
7. **QProgressBar**: Barra de progreso (oculta por defecto)
8. **QLabel**: Status (italic, gris)
9. **QGroupBox**: Contenedor "Configuración AST"
10. **QFormLayout**: Layout de formulario para alineación

**Características**:
- ✅ Ejecución asíncrona (no bloquea UI)
- ✅ Validación pre-simulación (bacteria profile, panel)
- ✅ Diálogo de confirmación con resumen
- ✅ Mensajes de progreso contextuales
- ✅ Manejo robusto de errores con QMessageBox
- ✅ Estilos CSS para botón y progress bar
- ✅ Tooltips informativos
- ✅ Auto-deshabilitación de controles durante simulación

**Integración**:
- Requiere `bacteria_profile_id` vía `set_bacteria_profile()`
- Emite `ast_completed(report)` al finalizar → conectar con ResultsTable
- Usa `ASTSimulator` completo (incubation → MICs → QC → report)



### 💡 NOTA PARA EL AGENTE (YO)
En el código del widget:
```python
self.organism_label = QLabel("Organismo: <b>Pseudomonas aeruginosa</b>")
self.organism_label.setEnabled(False)  # No editable
# NO crear ComboBox de organismos
```

---

## 📌 ITEM 3.2: Widget AST Plate Viewer
**Archivo**: `src/gui/widgets/ast_plate_viewer.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 3-4 horas

### Tareas
- [ ] Grid 8×12 (96 pocillos)
- [ ] Labels para filas (A-H) y columnas (1-12)
- [ ] Color por turbidez (blanco→amarillo→naranja)
- [ ] Tooltip con datos (antibiótico, conc, OD)
- [ ] Slider para ver evolución temporal
- [ ] Marcador de controles +/−

### Código de Colores
```python
def od_to_color(od_value):
    if od_value < 0.1:
        return "#ffffff"  # Blanco (claro)
    elif od_value < 0.5:
        return "#ffffcc"  # Amarillo claro
    elif od_value < 1.5:
        return "#ffcc00"  # Amarillo
    else:
        return "#cc9900"  # Naranja/turbio
```

---

## 📌 ITEM 3.3: Widget AST Results Table
**Archivo**: `src/gui/widgets/ast_results_table.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 2 horas

### Tareas
- [ ] QTableWidget con 6 columnas
- [ ] Cargar resultados desde BD (run_id)
- [ ] Colorear categorías (S=verde, I=amarillo, R=rojo)
- [ ] Botón exportar CSV
- [ ] Filtro por guideline (CLSI/EUCAST)

### Tabla Ejemplo
```
┌────────────────┬──────────┬──────────┬──────────┬────────┬────────┐
│ Antibiótico    │ MIC      │ Categoría│ Guideline│ BP S   │ BP R   │
├────────────────┼──────────┼──────────┼──────────┼────────┼────────┤
│ Meropenem      │ 4.0      │ I        │ CLSI-2025│ ≤2     │ ≥8     │
│ Ciprofloxacino │ ≥64      │ R        │ CLSI-2025│ ≤1     │ ≥4     │
│ Gentamicina    │ 1.0      │ S        │ CLSI-2025│ ≤4     │ ≥16    │
└────────────────┴──────────┴──────────┴──────────┴────────┴────────┘
```

---

## 📌 ITEM 3.4: Widget Growth Curves
**Archivo**: `src/gui/widgets/growth_curve_widget.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 💡 BAJA (Nice to have)  
**Estimación**: 2-3 horas

### Tareas
- [ ] PlotWidget (pyqtgraph)
- [ ] Eje X: Tiempo (horas)
- [ ] Eje Y: OD 600 nm
- [ ] Múltiples curvas por concentración
- [ ] Leyenda con concentraciones
- [ ] Línea vertical marcando MIC
- [ ] Selector de antibiótico

### Gráfico Ejemplo
```
OD
3.0 │         ╱─────  (0 µg/mL - Control +)
    │       ╱─────    (0.5 µg/mL)
2.0 │     ╱────       (1.0 µg/mL)
    │   ╱──           (2.0 µg/mL)
1.0 │ ╱──             (4.0 µg/mL) ← MIC
    │──               (8.0 µg/mL)
0.0 │────────────────────────────
    0    6    12   18  Tiempo (h)
```

---

## 📌 ITEM 3.5: Integrar en Main Window
**Archivo**: `src/gui/main_window.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1 hora

### Tareas
- [ ] Añadir tab "AST" al QTabWidget
- [ ] Integrar ASTPanelWidget
- [ ] Integrar ASTResultsTable
- [ ] Signal connections
- [ ] Menú "AST" en MenuBar

---

# FASE 4: VALIDACIÓN Y TESTING

## 📌 ITEM 4.1: Tests Unitarios AST
**Archivo**: `tests/test_ast_simulator.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 3-4 horas

### Tests a Implementar
- [ ] `test_mic_calculation_threshold()` - MIC correcto por umbral
- [ ] `test_mic_calculation_all_grow()` - MIC >= max cuando todas crecen
- [ ] `test_mic_calculation_none_grow()` - MIC <= min cuando ninguna crece
- [ ] `test_mic_interpolation()` - Interpolación en casos dudosos
- [ ] `test_growth_curve_logistic()` - Parámetros de curva válidos
- [ ] `test_growth_with_antibiotic()` - Inhibición correcta
- [ ] `test_measurement_noise()` - Ruido en rango aceptable

### Test Example
```python
def test_mic_calculation_threshold():
    """
    Caso: Bacteria crece en 0.5 µg/mL (OD=1.5)
          Bacteria NO crece en 1.0 µg/mL (OD=0.2)
    Esperado: MIC = 1.0 µg/mL
    """
    # Setup
    simulator = ASTSimulator(organism_id=1, panel_layout_id=1)
    simulator.create_run()
    
    # Mock well readings
    # Well 1: 0.5 µg/mL → OD_final = 1.5
    # Well 2: 1.0 µg/mL → OD_final = 0.2
    
    # Execute
    mic_value, mic_operator = simulator.calculate_mic_by_threshold(antibiotico_id=1)
    
    # Assert
    assert mic_value == 1.0
    assert mic_operator == '='
```

---

## 📌 ITEM 4.2: Tests de Interpretación S/I/R
**Archivo**: `tests/test_breakpoint_service.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 2 horas

### Tests a Implementar
- [ ] `test_interpret_mic_sensible()` - MIC ≤ BP_S → 'S'
- [ ] `test_interpret_mic_intermedio()` - BP_S < MIC < BP_R → 'I'
- [ ] `test_interpret_mic_resistente()` - MIC ≥ BP_R → 'R'
- [ ] `test_interpret_mic_censored_low()` - MIC <= min → 'S'
- [ ] `test_interpret_mic_censored_high()` - MIC >= max → 'R'
- [ ] `test_breakpoint_retrieval()` - Query correcto de BD

### Test Example
```python
def test_interpret_mic_sensible():
    """
    Caso: MIC = 1.0, BP_S = 2.0, BP_R = 8.0
    Esperado: 'S' (Sensible)
    """
    result = BreakpointService.interpret_mic(
        mic_value=1.0,
        mic_operator='=',
        breakpoint_s=2.0,
        breakpoint_r=8.0
    )
    assert result == 'S'
```

---

## 📌 ITEM 4.3: Tests de QC
**Archivo**: `tests/test_qc_validator.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 1-2 horas

### Tests a Implementar
- [ ] `test_positive_control_pass()` - OD > 0.5 → PASS
- [ ] `test_positive_control_fail()` - OD < 0.5 → FAIL
- [ ] `test_negative_control_pass()` - OD < 0.1 → PASS
- [ ] `test_negative_control_fail()` - OD > 0.1 → FAIL (contaminación)
- [ ] `test_coherence_carbapenems()` - Regla de coherencia

---

## 📌 ITEM 4.4: Tests de Integración
**Archivo**: `tests/test_ast_integration.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 2-3 horas

### Tests a Implementar
- [ ] `test_full_ast_workflow()` - Flujo completo end-to-end
- [ ] `test_run_persistence()` - Datos guardados en BD correctamente
- [ ] `test_breakpoint_coverage_validation()` - Panel cubre breakpoints
- [ ] `test_multiple_guidelines()` - CLSI vs EUCAST simultáneos

### Test Example
```python
def test_full_ast_workflow():
    """
    Test de flujo completo:
    1. Crear run
    2. Simular incubación
    3. Calcular MIC
    4. Interpretar S/I/R
    5. Validar QC
    6. Generar reporte
    """
    # 1. Create
    simulator = ASTSimulator(organism_id=1, panel_layout_id=1)
    run_id = simulator.create_run()
    
    # 2. Simulate
    simulator.simulate_incubation()
    
    # 3. Calculate MIC
    mic_results = simulator.calculate_all_mics()
    
    # 4. Interpret
    interpretations = simulator.interpret_results()
    
    # 5. QC
    qc_status = simulator.apply_qc_checks()
    assert qc_status == 'passed'
    
    # 6. Report
    report = simulator.get_report()
    assert 'organism_name' in report
    assert len(report['resultados']) > 0
```

---

# FASE 5: DOCUMENTACIÓN Y DISCLAIMER

## 📌 ITEM 5.1: Actualizar README
**Archivo**: `README.md`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 2 horas

### Secciones a Agregar
- [ ] ⚠️ ADVERTENCIA IMPORTANTE - Uso Educativo
- [ ] Descripción Módulo AST
- [ ] Descripción Módulo GA (separado)
- [ ] Tabla comparativa: Simulación vs Laboratorio Real
- [ ] Supuestos biológicos explícitos
- [ ] Fenómenos NO simulados
- [ ] Limitaciones del sistema
- [ ] Referencias normativas (CLSI/EUCAST)
- [ ] Casos de uso educativos sugeridos
- [ ] Declaración legal

### Disclaimer Obligatorio
```markdown
## ⚠️ ADVERTENCIA IMPORTANTE - USO EDUCATIVO

Este software incluye DOS módulos independientes:

### 1. Módulo AST (Antimicrobial Susceptibility Testing)
**Simula** el funcionamiento de sistemas automatizados como MicroScan/VITEK **de forma SIMPLIFICADA**.

#### 🔬 ALCANCE ESPECÍFICO
- **Organismo fijo**: *Pseudomonas aeruginosa* únicamente
- **NO identifica bacterias** (asume cultivo puro aislado previamente)
- **NO procesa muestras clínicas** (asume preparación completada)
- **Simula SOLO**: Panel AST → Incubación → Lectura → MIC → S/I/R

❌ **NO ES un dispositivo médico ni IVD (In Vitro Diagnostic)**
❌ **NO reemplaza** antibiogramas de laboratorio clínico
❌ **NO debe usarse** para guiar tratamientos médicos
❌ **NO tiene validación** regulatoria (FDA/CE/ANVISA)
❌ **NO simula** identificación bacteriana (MALDI-TOF/API/Vitek ID)
❌ **NO es multiorganismo** (solo P. aeruginosa)

✅ **USO APROPIADO**:
- Educación en microbiología clínica
- Demostración de principios de AST
- Investigación en metodologías de laboratorio
- Entrenamiento de estudiantes en interpretación de antibiogramas

**Breakpoints incluidos**: CLSI M100-2025 Table 2B y EUCAST v15.0 (solo *P. aeruginosa*, con fines educativos)

### 2. Módulo GA (Genetic Algorithm - Evolución de Resistencia)
Modelo computacional de evolución bacteriana bajo presión antibiótica.

✅ **USO APROPIADO**:
- Investigación en dinámica evolutiva
- Modelado de escenarios terapéuticos
- Educación en evolución y selección natural
```

---

## 📌 ITEM 5.2: Especificación Técnica AST
**Archivo**: `docs/AST_TECHNICAL_SPEC.md`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 2 horas

### Contenido
- [ ] Arquitectura del sistema (3 capas)
- [ ] Flujo de ejecución (diagrama)
- [ ] Modelo matemático de crecimiento (ecuaciones)
- [ ] Algoritmo de cálculo de MIC (pseudocódigo)
- [ ] Sistema de QC (criterios)
- [ ] Parámetros configurables (tabla)
- [ ] Breakpoints cargados (tabla resumen)
- [ ] Formato de reporte (JSON schema)

---

## 📌 ITEM 5.3: Fuentes de Breakpoints
**Archivo**: `docs/BREAKPOINTS_SOURCE.md`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 1 hora

### Contenido
- [ ] Referencia completa CLSI M100-2025
- [ ] Referencia completa EUCAST v13.1
- [ ] Tablas utilizadas (2A, 2B, 3A, 3B)
- [ ] Disclaimer oficial
- [ ] Diferencias CLSI vs EUCAST (tabla)
- [ ] Proceso de actualización de breakpoints

---

## 📌 ITEM 5.4: Guía de Usuario AST
**Archivo**: `docs/AST_USER_GUIDE.md`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 💡 BAJA (Nice to have)  
**Estimación**: 2-3 horas

### Contenido
- [ ] Introducción a AST
- [ ] Cómo ejecutar una simulación (paso a paso)
- [ ] Interpretación de resultados
- [ ] Troubleshooting (QC fallido, etc.)
- [ ] Casos de uso educativos
- [ ] FAQs
- [ ] Glosario de términos

---

# MÉTRICAS Y ESTIMACIONES

## Estimación Total de Esfuerzo (VERSIÓN FINAL REALISTA)

| Fase | Items | Horas Min | Horas Max | Promedio | Descripción |
|------|-------|-----------|-----------|----------|-------------|
| **FASE 0**: Reemplazo Hardware Físico | 3 | 5 | 7 | **6 h** | Generador bacteria, GUI escenario, BD |
| **FASE 1**: Modelo de Datos AST | 3 | 3 | 5 | **4 h** | Tablas panel/runs/wells/mic/breakpoints |
| **FASE 2**: Motor AST Core | 4 | 8 | 12 | **10 h** | Simulador, curvas, MIC, breakpoints |
| **FASE 3**: GUI Wizard | 5 | 7 | 11 | **9 h** | 7 páginas wizard |
| **FASE 4**: Integración GA | 2 | 6 | 10 | **8 h** | Pre-AST + Post-AST |
| **FASE 5**: Testing | 3 | 4 | 8 | **6 h** | Unit + Integration |
| **FASE 6**: Documentación | 3 | 4 | 7 | **5.5 h** | README + Manual + Specs |
| **TOTAL** | **23** | **37 h** | **60 h** | **48.5 h** | **~6 semanas a 8h/semana** |

### 📊 Comparación: Versión Anterior vs Final Realista

| Métrica | Versión Inflada | Versión Realista | Diferencia |
|---------|-----------------|------------------|------------|
| Items totales | 30 | 23 | **-23%** ✅ |
| Horas totales | 61.5h | **48.5h** | **-21%** ⚡ |
| Complejidad | Alta (multi-organism) | Media (P. aeruginosa) | -35% |
| Fases | 7 | 7 | Igual |
| **Factibilidad** | Media | **Alta** | ✅ |

**Reducción lograda**: -13 horas eliminando:
- ❌ Tabla organisms (hardcoded)
- ❌ Queries multi-organismo
- ❌ Features innecesarias
- ❌ Over-engineering GUI

---

## Priorización por Impacto

### 🔥 CRÍTICO (MVP - Minimum Viable Product)
**Objetivo**: Demostrar funcionalidad básica AST para *P. aeruginosa*  
**Tiempo estimado**: 18-22 horas (REDUCIDO por simplificación)

1. ✅ Modelo de datos básico sin tabla organisms (FASE 1)
2. ✅ ASTSimulator básico + Growth Models (FASE 2.1, 2.2)
3. ✅ Breakpoint Service simplificado (FASE 2.3)
4. ✅ Widget configuración (label fijo) + Tabla resultados (FASE 3.1, 3.3)
5. ✅ Tests unitarios core (FASE 4.1, 4.2)
6. ✅ README con disclaimer P. aeruginosa (FASE 5.1)

**Entregable MVP**:
- Ejecutar AST simulado para *Pseudomonas aeruginosa*
- Calcular MIC por umbral
- Interpretar S/I/R (CLSI únicamente, Table 2B)
- Mostrar tabla de resultados
- Disclaimer legal visible (organismo único)

---

### ⚠️ IMPORTANTE (Versión Completa)
**Objetivo**: Sistema completo con QC y múltiples guidelines  
**Tiempo estimado**: +12-15 horas (REDUCIDO)

7. ✅ QC Validator (FASE 2.4)
8. ✅ Plate Viewer (FASE 3.2)
9. ✅ Breakpoints EUCAST P. aeruginosa (FASE 1.2)
10. ✅ Tests de QC + Integración (FASE 4.3, 4.4)
11. ✅ Especificación técnica (FASE 5.2, 5.3)

---

### 💡 DESEABLE (Mejoras)
**Objetivo**: Features avanzadas y UX mejorada  
**Tiempo estimado**: +8-12 horas (REDUCIDO)

12. ✅ Growth Curves Widget (FASE 3.4)
13. ✅ Interpolación de MIC (FASE 2.1)
14. ✅ Guía de usuario (FASE 5.4)
15. ✅ Exportación PDF reportes AST
16. ✅ Comparación CLSI vs EUCAST side-by-side

---

## 🎯 RESUMEN DE SIMPLIFICACIONES

### ✂️ Eliminado (vs versión genérica)
1. ❌ Tabla `organisms` y clase `Organism`
2. ❌ Parámetro `organism_id` en métodos
3. ❌ ComboBox de selección de organismo en GUI
4. ❌ Identificación bacteriana (MALDI-TOF, API)
5. ❌ Tinción de Gram
6. ❌ Breakpoints multi-organismo (E. coli, S. aureus, etc.)
7. ❌ Validación de compatibilidad organismo-panel
8. ❌ Tests de casos edge multi-organismo

### ✅ Conservado (esencial MicroScan)
1. ✅ Paneles de microdilución 96 pocillos
2. ✅ Curvas de crecimiento (OD600, turbidez)
3. ✅ Cálculo de MIC (umbral + interpolación)
4. ✅ Interpretación S/I/R (CLSI/EUCAST)
5. ✅ Control de calidad (QC)
6. ✅ Series temporales (lecturas cada 60 min)
7. ✅ Breakpoints oficiales (Table 2B)
8. ✅ Reportes detallados

### 🎯 Ganancia
- **-22% código** (menos complejidad)
- **-11.5 horas** de desarrollo
- **+Foco** en P. aeruginosa (organismo más relevante en resistencia)
- **+Claridad** en alcance educativo

---

# CRITERIOS DE ACEPTACIÓN

## DoD (Definition of Done) por Item

### Para considerarse COMPLETADO, cada item debe:
- [ ] Código implementado y funcional
- [ ] Tests unitarios pasando (cobertura mínima 70%)
- [ ] Documentación inline (docstrings)
- [ ] Sin errores de linting (flake8, black)
- [ ] Commit con mensaje descriptivo
- [ ] Revisión de código (self-review)

### Para considerarse FASE COMPLETADA:
- [ ] Todos los items críticos completados
- [ ] Tests de integración pasando
- [ ] Documentación actualizada
- [ ] Demo funcional ejecutable

---

# 📊 RESUMEN FINAL Y PRÓXIMO PASO

## Decisiones Clave Documentadas

### ✅ Estándar de Breakpoints
- **Primario**: EUCAST v15.0 (2025) - Binario S/R (sin "Intermedio")
- **Fallback**: CLSI M07 (2023) - Solo si antibiótico falta en EUCAST
- **Fuente de datos**: CSV oficiales extraídos → migrados a tablas SQL
- **Razón**: Simplifica lógica, EUCAST más reciente, no somos clon de MicroScan

### ✅ Organismo Único
- **Especie**: *Pseudomonas aeruginosa* (hardcoded)
- **Justificación**: Bacteria crítica en resistencia hospitalaria, simplifica alcance MVP
- **Expansión futura**: Agregar organismos como nueva fase (fuera de este backlog)

### ✅ Panel de Antibióticos
- **Antibióticos**: 13 antibióticos desde `pseudomonas_aeruginosa_concentraciones_simuladas.csv`
- **Concentraciones**: Serie log₂ (0.25, 0.5, 1, 2, 4, 8, 16 µg/mL típico)
- **Total pozos**: ~100-120 pozos (13 antibióticos × promedio 8 concentraciones)
- **Layout**: Pre-cargado desde CSV → migración SQL (no generación dinámica)

### ✅ CSV → SQL (NO consumo directo)
- **Archivos fuente**:
  1. `eucast_pseudomonas_aeruginosa_v15_2025.csv` → tabla `breakpoints` (17 antibióticos)
  2. `pseudomonas_aeruginosa_concentraciones_simuladas.csv` → tabla `panel_layouts` (13 antibióticos, ~100 pozos)
  3. `familias_antibioticas_y_especies_base_utf8_bom.csv` → actualizar tabla `antibioticos` (metadatos)
  4. `pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv` → fallback en `breakpoints` (29 antibióticos)
  5. **`mutaciones_pseudomonas_aeruginosa_utf8_bom.csv`** → tabla `mutations` (11 mutaciones científicas) **[NUEVO]**
- **Proceso**: Migraciones SQL (015-020) cargan datos una sola vez
- **Validación**: No se consume CSV en runtime (solo durante setup)

### ✅ Fundamento Biológico de Resistencia **[NUEVO]**
**Fuente**: `mutaciones_pseudomonas_aeruginosa_utf8_bom.csv` (11 mutaciones con referencias CARD, PMID)

**Mecanismos documentados:**
1. **Alteración del blanco**: gyrA (T83I, ×8 MIC), parC (S87L, ×4 MIC), ftsI (YRIN, ×2 MIC)
2. **Pérdida de permeabilidad**: oprD (deleción, ×8 MIC carbapenem)
3. **Bombas de eflujo**: mexR (frameshift, ×4 MIC FQ), nalC (Q83K, ×2 MIC), mexZ (deleción, ×4 MIC AG)
4. **β-lactamasas**: ampC (promotor -32C→T, ×4 MIC), ampD (deleción, ×8 MIC), blaVIM/blaIMP (×32 MIC)

**Fitness cost documentado**: Baja/Media/Alta (usado en GA FASE 4)

**Integración**:
- `bacteria_profile_generator.py` (ITEM 0.4) consulta tabla `mutations` para generar genotipos realistas
- Incrementos MIC científicos (NO inventados): ×2, ×4, ×8, ×16, ×32
- GA (FASE 4) usa fitness_cost para penalizar mutaciones resistentes

---

## Métricas Actualizadas (VERSIÓN FINAL CON MUTACIONES)

| Fase | Items | Horas | Prioridad |
|------|-------|-------|-----------|
| **FASE 0**: Datos + Hardware Virtual | 8 | 10.0h | 🔥 CRÍTICA |
| **FASE 1**: Modelo de Datos (SQLAlchemy) | 3 | 1.5h | 🔥 CRÍTICA |
| **FASE 2**: Motor AST Core | 4 | 10.0h | 🔥 CRÍTICA |
| **FASE 3**: GUI Wizard | 5 | 9.0h | ⚠️ ALTA |
| **FASE 4**: Integración GA + Mutaciones | 2 | 8.0h | ⚠️ ALTA |
| **FASE 5**: Testing | 3 | 6.0h | ⚠️ MEDIA |
| **FASE 6**: Documentación | 3 | 5.5h | ⚠️ MEDIA |
| **TOTAL** | **28** | **50h** | - |

**Cambios respecto a versión anterior:**
- **+1 item**: Migración 016_seed_mutations.sql (FASE 0)
- **+0.5h**: bacteria_profile_generator.py más complejo (consulta tabla mutations)
- **+1 item FASE 0**: Total 8 items (antes 7)
- **Reducción FASE 1**: De 3h a 1.5h (solo modelos SQLAlchemy, migraciones SQL movidas a FASE 0)

**Justificación del tiempo:**
- Migraciones seed (CSV→SQL): 3.5h (breakpoints 1.5h + mutations 1h + panel 1h)
- Códigos científicos: 3h (bacteria_profile_generator con integración mutations)
- GUI: 2h (clinical_scenario_page)
- Tablas simples: 1h (familias 0.5h + bacteria_profiles 0.5h)
- **Total FASE 0**: 10h (crítico para calidad científica)  
**Razón del incremento:** 3 migraciones SQL adicionales (breakpoints, panel_layouts, familias)

---

## 🚀 PRÓXIMO PASO INMEDIATO (ACTUALIZADO)

**Comenzar FASE 0, ITEM 0.0:**  
`src/migrations/015_seed_breakpoints.sql` - Migración de breakpoints EUCAST

**Luego ITEM 0.1 (NUEVO):**  
`src/migrations/016_seed_mutations.sql` - Migración de mutaciones científicas (11 mutaciones con referencias PMID)

**Estrategia recomendada:**
1. ✅ Generar migraciones SQL con script Python desde CSV (velocidad)
2. ✅ Revisión manual de datos médicos críticos (calidad)
3. ✅ Validación con queries SQL (integridad)

**Orden de ejecución FASE 0:**
1. **015_seed_breakpoints.sql** (1.5h) - Fundamento S/R
2. **016_seed_mutations.sql** (1h) - Fundamento genético **[CRÍTICO PARA CALIDAD CIENTÍFICA]**
3. **017_seed_panel_layouts.sql** (1h) - Configuración panel AST
4. **019_update_antibioticos_familias.sql** (0.5h) - Metadatos educativos
5. **020_create_bacteria_profiles.sql** (0.5h) - Tabla auditoría

**¿Por qué ITEM 0.1 (mutations) es crítico?**
- Sin esta tabla, `bacteria_profile_generator.py` usaría valores hardcoded inventados
- Con esta tabla, usamos incrementos MIC científicos (×2, ×4, ×8, ×32) de publicaciones PMID
- Fitness cost documentado permite integración realista con GA (FASE 4)
- Referencias trazables (CARD, ResFinder, NCBI AMR)

**¿Procedo con ITEM 0.0 + ITEM 0.1 juntos (generación de ambas migraciones)?**

---

# NOTAS DE IMPLEMENTACIÓN

## Decisiones de Diseño

### 1. Separación Módulo AST vs GA
**Decisión**: Mantener completamente separados  
**Razón**: Son paradigmas diferentes (fenotípico vs evolutivo)  
**Implicación**: Dos tabs independientes en GUI

### 2. Organismo Único - *Pseudomonas aeruginosa*
**Decisión**: NO implementar tabla `organisms`, hardcodear P. aeruginosa  
**Razón**: Simplificar simulación, evitar complejidad de identificación  
**Implicación**: 
- -20% código en BD y lógica
- +Foco en antibióticos anti-pseudomonas
- Breakpoints solo Table 2B (CLSI)
**Trade-off**: Menos flexible, pero más educativo y mantenible

### 3. Almacenamiento de Series Temporales
**Decisión**: Tabla `well_readings` con lecturas cada 60 min  
**Razón**: Simular comportamiento real de MicroScan  
**Trade-off**: Más espacio en BD (500 KB/run) vs realismo

### 4. Cálculo de MIC: Umbral vs Interpolación
**Decisión**: Implementar ambos, usar umbral por defecto  
**Razón**: Umbral más simple y robusto, interpolación para casos edge  
**Uso**: Umbral 0.3 OD, interpolar si 0.1 < OD < 0.5

### 5. Breakpoints: CLSI y EUCAST
**Decisión**: Soportar ambos guidelines simultáneamente  
**Razón**: Educación comparativa  
**Implicación**: Usuario elige guideline en reporte  
**Fuentes**: CLSI Table 2B + EUCAST Pseudomonas spp.

### 6. Ruido en Mediciones
**Decisión**: ±5% CV (Coefficient of Variation)  
**Razón**: Típico de espectrofotómetros reales  
**Implementación**: Gaussiana centrada en 0, σ = 0.05 * OD

---

## Dependencias Externas

### Python Packages
- `numpy` >= 1.21.0 (curvas matemáticas) - ✅ Ya instalado
- `scipy` >= 1.7.0 (interpolación) - ⚠️ **VERIFICAR** si está en requirements.txt
- `SQLAlchemy` >= 1.4.0 (ORM) - ✅ Ya instalado
- `PyQt5` >= 5.15.0 (GUI) - ✅ Ya instalado
- `pyqtgraph` >= 0.12.0 (gráficos) - ✅ Ya instalado

### Datos Externos
- CLSI M100-2025 **Table 2B** (Non-Enterobacterales, incluye P. aeruginosa) - ⚠️ **Usar subset educativo**
- EUCAST v15.0 Pseudomonas spp. (libre, disponible en web) - ✅ Accesible
- **Archivo CSV existente**: `docs/pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv` - ✅ **YA DISPONIBLE**

---

## Checklist Pre-Implementación (ACTUALIZADO)

- [ ] Revisar estructura actual del proyecto
- [ ] Verificar versión de BD (última migración aplicada: `014_add_guest_to_simulations.sql`)
- [ ] Crear branch `feature/ast-module-pseudomonas`
- [ ] Configurar entorno de desarrollo
- [ ] Instalar dependencias faltantes (scipy si es necesario)
- [ ] **Leer CSV existente**: `docs/pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv`
- [ ] Leer CLSI M100 **Table 2B** únicamente
- [ ] Descargar EUCAST v15.0 Pseudomonas spp.
- [ ] ~~Preparar datos de test multi-organismo~~ **OMITIDO**
- [ ] Preparar datos de test: P. aeruginosa ATCC 27853 (cepa control QC)

---

## 💡 NOTAS FINALES PARA EL AGENTE (YO)

### Cuando implemente cualquier funcionalidad AST, RECORDAR:

1. **Organismo siempre es *Pseudomonas aeruginosa***
   ```python
   ORGANISM_NAME = "Pseudomonas aeruginosa"
   ORGANISM_GRAM = "negativo"
   ```

2. **NO crear parámetros organism_id**
   - ❌ `def create_run(organism_id, panel_id):`
   - ✅ `def create_run(panel_id):`

3. **Breakpoints solo Table 2B**
   - ❌ "CLSI M100 Table 2A" (Enterobacterales)
   - ✅ "CLSI M100 Table 2B" (P. aeruginosa)

4. **Archivo CSV ya existe**
   - Revisar `docs/pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv` antes de crear SQL

5. **Disclaimer siempre visible**
   - En README
   - En GUI (About dialog)
   - En reportes PDF/CSV

6. **Tests asumen P. aeruginosa**
   - No crear tests multi-organismo
   - Foco en antibióticos anti-pseudomonas

7. **Panel único**
   - "Pseudomonas Standard Panel" (no "Gram Negative")
   - Antibióticos: Carbapenems, Fluoroquinolonas, Aminoglicósidos, Cefalosporinas, Polimixinas

---

# GLOSARIO

**AST**: Antimicrobial Susceptibility Testing - Prueba de sensibilidad antimicrobiana  
**MIC**: Minimum Inhibitory Concentration - Concentración mínima inhibitoria  
**S/I/R**: Sensible / Intermedio / Resistente - Categorías de interpretación  
**CLSI**: Clinical and Laboratory Standards Institute - Organismo normativo (EE.UU.)  
**EUCAST**: European Committee on Antimicrobial Susceptibility Testing - Organismo normativo (Europa)  
**Breakpoint**: Punto de corte que separa S de I, e I de R  
**McFarland**: Escala de turbidez para estandarizar inóculo (0.5 = ~1.5×10⁸ CFU/mL)  
**OD**: Optical Density - Densidad óptica (turbidez medida)  
**OD600**: Densidad óptica medida a 600 nm (longitud de onda estándar)  
**QC**: Quality Control - Control de calidad  
**CFU**: Colony Forming Units - Unidades formadoras de colonias  
**IVD**: In Vitro Diagnostic - Dispositivo médico de diagnóstico in vitro

---

# CHANGELOG

## [No iniciado] - 2025-11-09
### Planeado
- FASE 1: Modelo de datos AST (4 items)
- FASE 2: Lógica de negocio (4 items)
- FASE 3: Interfaz gráfica (5 items)
- FASE 4: Testing (4 items)
- FASE 5: Documentación (4 items)

### Notas
- Backlog creado basado en auditoría completa del código
- Priorización: MVP primero (24-30h), luego versión completa
- Enfoque: Separación clara AST vs GA

---

**Última actualización**: 9 de noviembre de 2025  
**Responsable**: Agente de desarrollo SRB  
**Estado del proyecto**: 🔴 Análisis completado, implementación pendiente  
**Versión**: Realista (sin hardware físico, basado en MicroScan workflow desde panel en adelante)

---

# 🚀 SIGUIENTE PASO

**Acción inmediata**: Iniciar FASE 0, ITEM 0.1  
**Archivo a crear**: `src/core/bacteria_profile_generator.py`  
**Comando**: Crear generador de perfiles bacterianos (reemplazo de MALDI-TOF)  
**Tiempo estimado**: 2-3 horas  
**Contexto clave**: Este módulo reemplaza hardware físico que no tenemos, es innovación educativa

### Pre-requisito antes de empezar
1. ✅ Entender limitación física: NO tenemos muestra real, MALDI-TOF, ni incubadora
2. ✅ Solución: Usuario elige escenario clínico → Sistema genera bacteria in-silico
3. ✅ Desde panel AST en adelante → Copiamos workflow MicroScan real
4. ✅ Valor agregado: GA explica genética de resistencia (MicroScan NO hace esto)

**¿Proceder con FASE 0?** ✅ Listo para ejecutar con enfoque realista
