# BACKLOG DE IMPLEMENTACIÓN - MÓDULO AST
## Simulador de Resistencia Bacteriana (SRB)

**Fecha de creación**: 9 de noviembre de 2025  
**Última actualización**: 10 de noviembre de 2025  
**Objetivo**: Refactorizar aplicación + Implementar workflow AST completo para microbiólogos  
**Estado**: � EN PROGRESO (7% completado - 2/28 items)

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
| **FASE 0**: Datos + Hardware Reemplazo | 8 | 2 | 25% | � En Progreso |
| **FASE 1**: Modelo de Datos SQLAlchemy | 3 | 0 | 0% | 🔴 Pendiente |
| **FASE 2**: Motor AST Core | 4 | 0 | 0% | 🔴 Pendiente |
| **FASE 3**: GUI Wizard | 5 | 0 | 0% | 🔴 Pendiente |
| **FASE 4**: Integración GA + Mutaciones | 2 | 0 | 0% | 🔴 Pendiente |
| **FASE 5**: Testing | 3 | 0 | 0% | 🔴 Pendiente |
| **FASE 6**: Documentación | 3 | 0 | 0% | 🔴 Pendiente |
| **TOTAL** | **28** | **2** | **7%** | � INICIADO |

---

# FASE 0: DATOS FUNDACIONALES + HARDWARE VIRTUAL (INNOVACIÓN)

## 📌 ITEM 0.0: Migración de Breakpoints (EUCAST)
**Archivo**: `src/migrations/015_seed_breakpoints.sql`  
**Estado**: ✅ COMPLETADO (10-nov-2025)  
**Prioridad**: 🔥 CRÍTICA (Fundamento de interpretación S/R)  
**Estimación**: 1.5 horas  
**Tiempo real**: 1.5 horas

### ⚠️ CONTEXTO - DECISIÓN DE ESTÁNDAR
**Estándar primario:** EUCAST v15.0 (2025) - más reciente, simplificado (sin categoría "I")  
**Estándar fallback:** CLSI M07 (2023) - solo si antibiótico no está en EUCAST  
**Fuente de datos:** `docs/eucast_pseudomonas_aeruginosa_v15_2025.csv` (17 antibióticos)

**Razón**: EUCAST es binario (S/R), elimina complejidad de "Intermedio". MicroScan usa ambos, pero nosotros no somos clon.

### Tareas
- [x] Crear script `scripts/generate_breakpoints_migration.py`
- [x] Crear tabla `breakpoints` con 8 columnas (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo)
- [x] Insertar 17 antibióticos desde EUCAST CSV
- [x] Agregar 6 fallbacks desde CLSI para antibióticos no cubiertos por EUCAST
- [x] Incluir queries de validación en migración SQL
- [x] Total: 23 breakpoints generados (17 EUCAST + 6 CLSI)

### Resultados
- Archivo generado: `src/migrations/015_seed_breakpoints.sql` (7615 caracteres, 88 líneas)
- Validación incluida: 3 queries SQL comentadas para verificar integridad
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
  ```sql
  CREATE TABLE IF NOT EXISTS gene_class_multipliers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      gen TEXT NOT NULL,                      -- 'gyrA_T83I', 'oprD_loss', etc.
      clase_antibiotico TEXT NOT NULL,        -- 'carbapenemicos', 'fluoroquinolonas', etc.
      multiplicador_mic REAL NOT NULL,        -- 1.0, 2.0, 4.0, 8.0, 16.0
      UNIQUE(gen, clase_antibiotico)
  );
  ```

- [ ] Insertar 99 combinaciones desde matriz CSV:
  ```sql
  INSERT INTO gene_class_multipliers (gen, clase_antibiotico, multiplicador_mic) VALUES
  -- Carbapenemicos
  ('gyrA_T83I', 'carbapenemicos', 1.0),
  ('parC_S87L', 'carbapenemicos', 1.0),
  ('oprD_loss', 'carbapenemicos', 8.0),
  ('ampC_promoter_-32C_T', 'carbapenemicos', 1.0),
  ('ampD_loss', 'carbapenemicos', 1.0),
  ('mexR_frameshift', 'carbapenemicos', 1.0),
  ('nalC_Q83K', 'carbapenemicos', 1.0),
  ('mexZ_loss', 'carbapenemicos', 1.0),
  ('ftsI_PBP3_insertion_YRIN', 'carbapenemicos', 2.0),
  ('blaVIM_or_blaIMP', 'carbapenemicos', 16.0),
  ('pmrB_mut', 'carbapenemicos', 1.0),
  
  -- Fluoroquinolonas (casos críticos)
  ('gyrA_T83I', 'fluoroquinolonas', 8.0),     -- ×8 MIC Cipro
  ('parC_S87L', 'fluoroquinolonas', 4.0),     -- ×4 MIC Cipro
  ('mexR_frameshift', 'fluoroquinolonas', 4.0), -- Bomba eflujo
  ('nalC_Q83K', 'fluoroquinolonas', 2.0),
  
  -- Aminoglucosidos
  ('mexZ_loss', 'aminoglucosidos', 4.0),      -- MexXY-OprM
  
  -- Polimixinas
  ('pmrB_mut', 'polimixinas', 8.0),           -- Resistencia colistina
  
  -- ... (continuar con las 99 filas del CSV)
  ```

- [ ] Crear tabla auxiliar `antibiotic_classes` (mapeo antibiótico → clase):
  ```sql
  CREATE TABLE IF NOT EXISTS antibiotic_classes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      antibiotico TEXT NOT NULL,
      clase TEXT NOT NULL,                     -- Referencia a gene_class_multipliers.clase_antibiotico
      UNIQUE(antibiotico)
  );
  
  INSERT INTO antibiotic_classes (antibiotico, clase) VALUES
  ('Meropenem', 'carbapenemicos'),
  ('Imipenem', 'carbapenemicos'),
  ('Doripenem', 'carbapenemicos'),
  ('Ceftazidima', 'cef_3G_ceftazidima'),
  ('Cefepime', 'cef_4G_cefepime'),
  ('Ceftazidima/Avibactam', 'cef_inhibidor'),
  ('Ceftolozano/Tazobactam', 'cef_inhibidor'),
  ('Aztreonam', 'monobactam_aztreonam'),
  ('Piperacilina/Tazobactam', 'penicilina_inhibidor'),
  ('Amikacina', 'aminoglucosidos'),
  ('Tobramicina', 'aminoglucosidos'),
  ('Ciprofloxacino', 'fluoroquinolonas'),
  ('Levofloxacino', 'fluoroquinolonas'),
  ('Colistina', 'polimixinas'),
  ('Cefiderocol', 'sideroforo_cefiderocol');
  ```

### 💡 VALIDACIÓN
```sql
-- Verificar genes con mayor impacto en carbapenem
SELECT gen, multiplicador_mic 
FROM gene_class_multipliers 
WHERE clase_antibiotico='carbapenemicos' AND multiplicador_mic > 1 
ORDER BY multiplicador_mic DESC;
-- Debe retornar: blaVIM (16), oprD_loss (8), ftsI (2)

-- Verificar genes con mayor impacto en fluoroquinolonas
SELECT gen, multiplicador_mic 
FROM gene_class_multipliers 
WHERE clase_antibiotico='fluoroquinolonas' AND multiplicador_mic > 1 
ORDER BY multiplicador_mic DESC;
-- Debe retornar: gyrA_T83I (8), parC_S87L (4), mexR (4), nalC (2)
```

---

## 📌 ITEM 0.2: Migración de Panel Layouts
**Archivo**: `src/migrations/017_seed_panel_layouts.sql`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (Define concentraciones del panel AST)  
**Estimación**: 1 hora

### ⚠️ CONTEXTO
**Fuente:** `docs/pseudomonas_aeruginosa_concentraciones_simuladas.csv` (13 antibióticos)  
**Serie log₂:** Cada antibiótico tiene 7-9 pozos con concentraciones duplicadas (0.25 → 0.5 → 1 → 2 → 4 → 8 → 16)  
**Total pozos estimados:** ~100-120 pozos (13 antibióticos × promedio 8 concentraciones)

### Tareas
- [ ] Script Python temporal para generar INSERTs desde CSV:
  ```python
  # scripts/generate_panel_inserts.py (ejecutar manualmente, luego borrar)
  import csv
  
  panel_name = 'PA_Standard_Panel_v1'
  row_letter = 'A'
  
  with open('docs/pseudomonas_aeruginosa_concentraciones_simuladas.csv') as f:
      reader = csv.DictReader(f)
      for row in reader:
          min_c = float(row['Rango_Min'])
          max_c = float(row['Rango_Max'])
          
          # Generar serie log₂
          concentrations = []
          conc = min_c
          while conc <= max_c:
              concentrations.append(conc)
              conc *= 2
          
          # Generar INSERTs
          for i, conc in enumerate(concentrations):
              well_pos = f"{row_letter}{i+1}"
              print(f"('{panel_name}', '{row['Antibiotico']}', '{well_pos}', {conc}),")
          
          row_letter = chr(ord(row_letter) + 1)
  ```

- [ ] Pegar output en migración 016:
  ```sql
  INSERT INTO panel_layouts (panel_name, antibiotico, well_position, concentration_ug_ml) VALUES
  ('PA_Standard_Panel_v1', 'Meropenem', 'A1', 0.25),
  ('PA_Standard_Panel_v1', 'Meropenem', 'A2', 0.5),
  -- ... (~100 filas más)
  ```

### 💡 VALIDACIÓN
`SELECT antibiotico, COUNT(*) FROM panel_layouts GROUP BY antibiotico;` → Cada antibiótico debe tener 7-9 pozos

---

## 📌 ITEM 0.2: Migración de Familias Antibióticas
**Archivo**: `src/migrations/017_update_antibioticos_familias.sql`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA (Metadatos educativos)  
**Estimación**: 0.5 horas

### Tareas
- [ ] Agregar columnas a tabla `antibioticos` existente:
  ```sql
  ALTER TABLE antibioticos ADD COLUMN familia TEXT;
  ALTER TABLE antibioticos ADD COLUMN mecanismo_accion TEXT;
  ```

- [ ] Seed desde `familias_antibioticas_y_especies_base_utf8_bom.csv`:
  ```sql
  UPDATE antibioticos SET familia='Carbapenémico', mecanismo_accion='Inhibe síntesis de pared bacteriana' WHERE nombre='Meropenem';
  UPDATE antibioticos SET familia='Carbapenémico', mecanismo_accion='Inhibe síntesis de pared bacteriana' WHERE nombre='Imipenem';
  -- ... (13 antibióticos)
  ```

---

---

## 📌 ITEM 0.4: Generador de Perfiles Bacterianos (CIENTÍFICO)
**Archivo**: `src/core/bacteria_profile_generator.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (Reemplaza MALDI-TOF + preparación física)  
**Estimación**: 3 horas (aumentado por integración con tabla mutations)

### ⚠️ CONTEXTO IMPORTANTE
**En MicroScan real**: Técnico toma muestra física → MALDI-TOF identifica bacteria → Prepara inóculo  
**En nuestra app**: Usuario elige escenario clínico → Sistema genera bacteria in-silico

**Esto NO es una limitación, es una FEATURE educativa**:
- ✅ Usuario puede explorar diferentes escenarios sin esperar cultivos
- ✅ Sistema explica genotipo (MicroScan NO hace esto)
- ✅ **Mutaciones basadas en datos científicos reales** (CARD, NCBI AMR)

### Tareas

- [ ] Constante global: `ORGANISM_NAME = "Pseudomonas aeruginosa"`

- [ ] Método `generate_wild_type()` - Bacteria comunitaria sensible
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
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA  
**Estimación**: 2 horas

### Tareas
- [ ] Clase `ClinicalScenarioPage(QWizardPage)`
- [ ] Dropdown: Origen de muestra (Hemocultivo/Esputo/Orina)
- [ ] RadioButton: Comunitario vs Hospitalizado
- [ ] CheckList (solo si Hospitalizado): Antibióticos previos
- [ ] Botón: "Generar Bacteria" → Llama a `bacteria_profile_generator`
- [ ] Label: Mostrar genotipo generado (educativo)

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
**Archivo**: `src/migrations/019_update_antibioticos_familias.sql`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA (Metadatos educativos)  
**Estimación**: 0.5 horas

### Tareas
- [ ] Agregar columnas a tabla `antibioticos` existente:
  ```sql
  ALTER TABLE antibioticos ADD COLUMN familia TEXT;
  ALTER TABLE antibioticos ADD COLUMN mecanismo_accion TEXT;
  ```

- [ ] Seed desde `familias_antibioticas_y_especies_base_utf8_bom.csv`:
  ```sql
  UPDATE antibioticos SET familia='Carbapenémico', mecanismo_accion='Inhibe síntesis de pared bacteriana' WHERE nombre='Meropenem';
  UPDATE antibioticos SET familia='Carbapenémico', mecanismo_accion='Inhibe síntesis de pared bacteriana' WHERE nombre='Imipenem';
  -- ... (13 antibióticos)
  ```

---

## 📌 ITEM 0.7: Tabla bacteria_profiles
**Archivo**: `src/migrations/020_create_bacteria_profiles.sql`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 0.5 horas

### Tareas
- [ ] Crear tabla para almacenar perfiles generados:
  ```sql
  CREATE TABLE IF NOT EXISTS bacteria_profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      organismo TEXT NOT NULL DEFAULT 'Pseudomonas aeruginosa',
      escenario TEXT NOT NULL,           -- 'comunitario' o 'hospitalizado'
      origen_muestra TEXT,                -- 'hemocultivo', 'esputo', 'orina'
      antibioticos_previos TEXT,          -- JSON: ['Ciprofloxacino', 'Meropenem']
      genotipo TEXT NOT NULL,             -- JSON: {'gyrA': 'Sustitución T83I', 'oprD': 'Deleción'}
      mics_base TEXT NOT NULL,            -- JSON: {'Meropenem': 16.0, 'Cipro': 32.0}
      mutaciones_aplicadas TEXT,          -- JSON: [{'gen': 'gyrA', 'fitness_cost': 'Media'}]
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

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

## 📌 ITEM 1.1: Modelo Mutation (Genética de Resistencia)
**Archivo**: `src/data/models.py` (agregar a archivo existente)  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (Fundamento científico)  
**Estimación**: 0.5 horas

### Tareas
- [ ] Agregar clase `Mutation` a `models.py`:
  ```python
  from sqlalchemy import Column, Integer, String, Text
  
  class Mutation(Base):
      __tablename__ = 'mutations'
      
      id = Column(Integer, primary_key=True)
      gen = Column(String(50), nullable=False)
      tipo_mutacion = Column(String(100), nullable=False)
      mecanismo = Column(Text, nullable=False)
      antibioticos_afectados = Column(Text, nullable=False)  # JSON array
      incremento_mic_factor = Column(Integer, nullable=False)
      fitness_cost = Column(String(20), nullable=False)  # 'Baja', 'Media', 'Alta'
      fuente = Column(Text, nullable=False)
      
      def __repr__(self):
          return f"<Mutation {self.gen} ({self.tipo_mutacion})>"
  ```

### 💡 INTEGRACIÓN
Este modelo es usado por `bacteria_profile_generator.py` (ITEM 0.4) para aplicar mutaciones científicas.

---

## 📌 ITEM 1.2: Modelo Breakpoint (Puntos de Corte)
**Archivo**: `src/data/models.py` (agregar a archivo existente)  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (Interpretación S/R)  
**Estimación**: 0.5 horas

### Tareas
- [ ] Agregar clase `Breakpoint` a `models.py`:
  ```python
  from sqlalchemy import Column, Integer, String, Float, Text
  
  class Breakpoint(Base):
      __tablename__ = 'breakpoints'
      
      id = Column(Integer, primary_key=True)
      antibiotico = Column(String(100), nullable=False)
      organismo = Column(String(100), nullable=False, default='Pseudomonas aeruginosa')
      s_mic = Column(Float, nullable=False)
      r_mic = Column(Float, nullable=False)
      standard = Column(String(20), nullable=False)  # 'EUCAST' o 'CLSI'
      fuente = Column(Text, nullable=False)
      familia = Column(String(100))
      mecanismo = Column(Text)
      
      def interpret_mic(self, mic_value):
          """Retorna 'S' o 'R' según MIC."""
          if mic_value <= self.s_mic:
              return 'S'
          elif mic_value > self.r_mic:
              return 'R'
          else:
              # EUCAST no tiene 'I', pero por si acaso
              return 'R'  # Conservador
      
      def __repr__(self):
          return f"<Breakpoint {self.antibiotico} S≤{self.s_mic} R>{self.r_mic}>"
  ```

---

## 📌 ITEM 1.3: Modelo BacteriaProfile (Perfiles Bacterianos)
**Archivo**: `src/data/models.py` (agregar a archivo existente)  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 0.5 horas

### Tareas
- [ ] Agregar clase `BacteriaProfile` a `models.py`:
  ```python
  from sqlalchemy import Column, Integer, String, Text, DateTime
  from datetime import datetime
  
  class BacteriaProfile(Base):
      __tablename__ = 'bacteria_profiles'
      
      id = Column(Integer, primary_key=True)
      organismo = Column(String(100), nullable=False, default='Pseudomonas aeruginosa')
      escenario = Column(String(50), nullable=False)  # 'comunitario', 'hospitalizado'
      origen_muestra = Column(String(50))  # 'hemocultivo', 'esputo', 'orina'
      antibioticos_previos = Column(Text)  # JSON array
      genotipo = Column(Text, nullable=False)  # JSON dict
      mics_base = Column(Text, nullable=False)  # JSON dict
      mutaciones_aplicadas = Column(Text)  # JSON array
      created_at = Column(DateTime, default=datetime.utcnow)
      
      def __repr__(self):
          return f"<BacteriaProfile {self.organismo} ({self.escenario})>"
  ```

---

**ESTIMACIÓN TOTAL FASE 1:** 1.5 horas (3 modelos nuevos en models.py)

**NOTA**: Las tablas SQL correspondientes ya fueron creadas en FASE 0 (migraciones 016, 015, 020).

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
**Archivo**: `src/migrations/016_seed_breakpoints.sql`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1-2 horas (SIMPLIFICADO - solo P. aeruginosa)

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
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 1 hora (SIMPLIFICADO)

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
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1 hora (SIMPLIFICADO - sin clase Organism)

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
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 4-6 horas (SIMPLIFICADO)

### Tareas
- [ ] Definir constantes globales
  ```python
  ORGANISM_NAME = "Pseudomonas aeruginosa"
  ORGANISM_GRAM = "negativo"
  DEFAULT_TEMPERATURE = 37.0  # °C
  DEFAULT_INOCULUM = 0.5      # McFarland
  DEFAULT_DURATION = 18       # horas
  ```

- [ ] Clase `ASTSimulator.__init__(panel_layout_id, inoculo_mcfarland=0.5, temperatura=37.0)`
  - **SIN parámetro organism_id** (siempre P. aeruginosa)
  
- [ ] Método `create_run()` - Crear run en BD + pocillos
- [ ] Método `simulate_incubation()` - Simular 18h de incubación
- [ ] Método `calculate_growth_curve(well)` - Curva logística por pocillo
- [ ] Método `read_wells_at_time(time_minutes)` - Lectura óptica simulada
- [ ] Método `calculate_mic_by_threshold(antibiotico_id)` - Algoritmo umbral
- [ ] Método `calculate_mic_by_interpolation(antibiotico_id)` - Interpolación
- [ ] Método `apply_qc_checks()` - Validar controles +/−
- [ ] Método `interpret_results(guideline='CLSI')` - Mapeo MIC → S/I/R
- [ ] Método `get_report()` - Generar reporte completo

### 💡 NOTA PARA EL AGENTE (YO)
En `get_report()`, SIEMPRE incluir:
```python
{
  "organism": ORGANISM_NAME,  # Hardcoded
  "organism_gram": ORGANISM_GRAM,
  # ... resto del reporte
}
```

### Algoritmo Clave: Cálculo MIC por Umbral
```python
def calculate_mic_by_threshold(self, antibiotico_id):
    """
    1. Obtener pocillos con ese antibiótico, ordenados por concentración
    2. Definir umbral OD (típico 0.3)
    3. Encontrar primera concentración con OD_final < umbral
    4. Esa es el MIC
    5. Casos especiales:
       - Todas crecen (OD > umbral): MIC >= max_conc
       - Ninguna crece: MIC <= min_conc
    """
    umbral = 0.3
    wells_ordenados = sorted(wells, key=lambda w: w.concentracion_ug_ml)
    
    for well in wells_ordenados:
        od_final = get_last_reading(well).od_600
        if od_final < umbral:
            return well.concentracion_ug_ml, '='
    
    # Todas crecen
    return wells_ordenados[-1].concentracion_ug_ml, '>='
```

### Parámetros de Curva de Crecimiento
- `od_initial`: 0.05 (inóculo 0.5 McFarland)
- `od_max`: 2.0 (bacteria típica sin antibiótico)
- `k`: 0.02 min⁻¹ (tasa de crecimiento)
- `t_mid`: 480 min (8 horas, punto de inflexión)

---

## 📌 ITEM 2.2: Módulo Growth Models
**Archivo**: `src/core/growth_models.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 2-3 horas

### Tareas
- [ ] Función `logistic_growth(t, od_max, k, t_mid, od_initial)`
- [ ] Función `calculate_od_max_with_antibiotic(base_od_max, concentration, mic_real)`
- [ ] Función `add_measurement_noise(od_value, noise_level=0.05)`
- [ ] Función `classify_turbidity(od_value)` → 'claro', 'ligero', 'moderado', 'turbio'

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

---

## 📌 ITEM 2.3: Módulo Breakpoint Service
**Archivo**: `src/core/breakpoint_service.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1.5 horas (SIMPLIFICADO)

### Tareas
- [ ] Método `get_breakpoint(antibiotico_id, guideline='CLSI', version='M100-2025')`
  - **SIN parámetro organism_id** (siempre P. aeruginosa)
  - Query directo a tabla `breakpoints` filtrado solo por antibiotico_id
  
- [ ] Método `interpret_mic(mic_value, mic_operator, breakpoint_s, breakpoint_r)`
- [ ] Método `check_breakpoint_coverage(panel_layout_id, antibiotico_id)`
- [ ] Cacheo de breakpoints frecuentes

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

---

## 📌 ITEM 2.4: Módulo QC Validator
**Archivo**: `src/core/qc_validator.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: ⚠️ MEDIA  
**Estimación**: 2 horas

### Tareas
- [ ] Método `validate_positive_control(run_id)` - OD > 0.5
- [ ] Método `validate_negative_control(run_id)` - OD < 0.1
- [ ] Método `validate_coherence(run_id)` - Antibióticos relacionados
- [ ] Método `generate_qc_report(run_id)`

### Reglas de Coherencia
```python
COHERENCE_RULES = {
    'carbapenems': ['Imipenem', 'Meropenem', 'Ertapenem'],
    # Si Imipenem R → Meropenem probablemente R (mismo mecanismo)
    
    'fluoroquinolonas': ['Ciprofloxacino', 'Levofloxacino'],
    # Resistencia cruzada común
}
```

---

# FASE 3: INTERFAZ DE USUARIO (GUI)

## 📌 ITEM 3.1: Widget AST Panel
**Archivo**: `src/gui/widgets/ast_panel_widget.py`  
**Estado**: 🔴 Pendiente  
**Prioridad**: 🔥 CRÍTICA (MVP)  
**Estimación**: 1.5-2 horas (SIMPLIFICADO)

### Tareas
- [x] ~~ComboBox para selección de organismo~~ **OMITIDO** (siempre P. aeruginosa)
  - Mostrar label fijo: "Organismo: *Pseudomonas aeruginosa*"
  
- [ ] ComboBox para selección de panel
  - Cargar desde BD (tabla `panel_layouts`)
  - Por defecto: "Pseudomonas Standard Panel"
  
- [ ] SpinBox para inóculo (McFarland)
  - Rango: 0.3 - 0.7 (típico 0.5)
  
- [ ] SpinBox para temperatura
  - Rango: 35-37°C (fijo en mayoría de casos)
  
- [ ] SpinBox para duración
  - Fijo: 18.0 horas (estándar AST)
  
- [ ] Botón "Ejecutar AST"
- [ ] ProgressBar durante simulación
- [ ] Signal `ast_completed(run_id)`

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
