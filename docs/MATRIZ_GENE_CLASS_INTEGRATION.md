# 🧬 INTEGRACIÓN MATRIZ GEN × CLASE - ACTUALIZACIÓN CRÍTICA

**Fecha**: 10 de noviembre de 2025  
**Propósito**: Documento complementario a AST_IMPLEMENTATION_BACKLOG.md  
**Cambio crítico**: Reemplazar tabla `mutations` simple por sistema matricial gen × clase

---

## 🔬 FUNDAMENTO CIENTÍFICO MEJORADO

### ❌ **Problema con enfoque anterior:**
- CSV `mutaciones_pseudomonas_aeruginosa.csv` tenía **incremento MIC global**
- Ejemplo: `gyrA T83I → ×8 MIC` para **TODOS** los antibióticos
- **Biológicamente incorrecto**: gyrA afecta fluoroquinolonas, NO carbapenem

### ✅ **Solución con matriz:**
- CSV `matriz_genes_x_clases_MIC_multiplicadores_LONG_utf8_bom.csv`
- **11 genes × 9 clases** = 99 combinaciones específicas
- Ejemplo: `gyrA_T83I × fluoroquinolonas = ×8`, pero `gyrA_T83I × carbapenemicos = ×1` (sin efecto)

---

## 📊 ESTRUCTURA DE LA MATRIZ

```csv
gen,clase,multiplicador_MIC
gyrA_T83I,fluoroquinolonas,8.0
gyrA_T83I,carbapenemicos,1.0
oprD_loss,carbapenemicos,8.0
oprD_loss,fluoroquinolonas,1.0
blaVIM_or_blaIMP,carbapenemicos,16.0
mexZ_loss,aminoglucosidos,4.0
pmrB_mut,polimixinas,8.0
```

**Clases de antibióticos:**
1. `carbapenemicos` - Meropenem, Imipenem, Doripenem
2. `cef_3G_ceftazidima` - Ceftazidima
3. `cef_4G_cefepime` - Cefepime
4. `cef_inhibidor` - Ceftazidima/Avibactam, Ceftolozano/Tazobactam
5. `monobactam_aztreonam` - Aztreonam
6. `penicilina_inhibidor` - Piperacilina/Tazobactam
7. `aminoglucosidos` - Amikacina, Tobramicina
8. `fluoroquinolonas` - Ciprofloxacino, Levofloxacino
9. `polimixinas` - Colistina
10. `sideroforo_cefiderocol` - Cefiderocol

**Genes documentados:**
- `gyrA_T83I`, `parC_S87L` - Alteración blanco (ADN girasa/topoisomerasa)
- `oprD_loss` - Pérdida porina OprD
- `ampC_promoter_-32C_T`, `ampD_loss` - β-lactamasas AmpC
- `mexR_frameshift`, `nalC_Q83K`, `mexZ_loss` - Bombas de eflujo
- `ftsI_PBP3_insertion_YRIN` - Alteración PBP3
- `blaVIM_or_blaIMP` - Metalobetalactamasa
- `pmrB_mut` - Resistencia polimixinas

---

## 🧮 REGLA DE ACUMULACIÓN

**Cuando bacteria tiene múltiples mutaciones:**

```python
MIC_final = MIC_base × mult_gen1 × mult_gen2 × ... × mult_genN
```

**Ejemplo 1 - Bacteria con `oprD_loss` + `blaVIM`:**
- Antibiótico: Meropenem (clase: `carbapenemicos`)
- MIC_base: 0.5 µg/mL
- oprD_loss × carbapenemicos: ×8 → 4.0 µg/mL
- blaVIM × carbapenemicos: ×16 → **64.0 µg/mL**
- Interpretación: **Resistente** (EUCAST R > 8)

**Ejemplo 2 - Bacteria con `gyrA_T83I` + `parC_S87L` + `mexR_frameshift`:**
- Antibiótico: Ciprofloxacino (clase: `fluoroquinolonas`)
- MIC_base: 0.25 µg/mL
- gyrA_T83I: ×8 → 2.0
- parC_S87L: ×4 → 8.0
- mexR_frameshift: ×4 → **32.0 µg/mL**
- Interpretación: **Resistente** (EUCAST R > 0.5)

**Ejemplo 3 - Bacteria con `mexZ_loss` solamente:**
- Antibiótico: Amikacina (clase: `aminoglucosidos`)
- MIC_base: 4.0 µg/mL
- mexZ_loss × aminoglucosidos: ×4 → **16.0 µg/mL**
- Interpretación: **Sensible** (EUCAST S ≤ 16)

---

## 🔄 CAMBIOS NECESARIOS EN BACKLOG

### 1. **FASE 0, ITEM 0.1** - Cambiar migración

**Antes:**
```sql
CREATE TABLE mutations (
    gen TEXT,
    incremento_mic_factor INTEGER,  -- ❌ Global
    ...
);
```

**Después:**
```sql
CREATE TABLE gene_class_multipliers (
    gen TEXT,
    clase_antibiotico TEXT,
    multiplicador_mic REAL,  -- ✅ Específico por clase
    UNIQUE(gen, clase_antibiotico)
);

CREATE TABLE antibiotic_classes (
    antibiotico TEXT,
    clase TEXT,
    UNIQUE(antibiotico)
);
```

### 2. **FASE 0, ITEM 0.4** - bacteria_profile_generator.py

**Antes:**
```python
# Hardcoded
if 'Ciprofloxacino' in antibioticos_previos:
    mics['Ciprofloxacino'] *= 8  # ❌ Valor inventado
```

**Después:**
```python
# Consulta matriz
for antibiotico, mic_base in mics.items():
    clase = get_antibiotic_class(antibiotico)
    mult_total = 1.0
    
    for gene in active_mutations:
        mult = query_multiplier(gene, clase)
        mult_total *= mult
    
    mics[antibiotico] = min(mic_base * mult_total, 64.0)
```

### 3. **FASE 1, ITEM 1.1** - Modelos SQLAlchemy

**Agregar:**
```python
class GeneClassMultiplier(Base):
    __tablename__ = 'gene_class_multipliers'
    gen = Column(String(100))
    clase_antibiotico = Column(String(50))
    multiplicador_mic = Column(Float)

class AntibioticClass(Base):
    __tablename__ = 'antibiotic_classes'
    antibiotico = Column(String(100))
    clase = Column(String(50))
```

---

## 📈 IMPACTO EN MÉTRICAS

**Cambios estimados:**
- FASE 0, ITEM 0.1: +0.5h (matriz más compleja que tabla simple)
- FASE 0, ITEM 0.4: +1h (lógica de acumulación)
- FASE 1: +0.5h (2 modelos adicionales)

**Total incremento:** +2h → **52 horas totales**

---

## ✅ VALIDACIÓN CIENTÍFICA

**Query de validación 1 - Genes críticos en carbapenem:**
```sql
SELECT gen, multiplicador_mic 
FROM gene_class_multipliers 
WHERE clase_antibiotico='carbapenemicos' AND multiplicador_mic > 1 
ORDER BY multiplicador_mic DESC;
```
**Resultado esperado:**
- blaVIM_or_blaIMP: 16.0
- oprD_loss: 8.0
- ftsI_PBP3_insertion_YRIN: 2.0

**Query de validación 2 - Genes críticos en fluoroquinolonas:**
```sql
SELECT gen, multiplicador_mic 
FROM gene_class_multipliers 
WHERE clase_antibiotico='fluoroquinolonas' AND multiplicador_mic > 1 
ORDER BY multiplicador_mic DESC;
```
**Resultado esperado:**
- gyrA_T83I: 8.0
- parC_S87L: 4.0
- mexR_frameshift: 4.0
- nalC_Q83K: 2.0

---

## 🎯 PRÓXIMOS PASOS

1. **Actualizar AST_IMPLEMENTATION_BACKLOG.md:**
   - ITEM 0.1: Reemplazar `mutations` por `gene_class_multipliers`
   - ITEM 0.4: Agregar lógica de acumulación matricial
   - Métricas: 28 items, 52h

2. **Proceder con implementación:**
   - Generar migración 016_seed_gene_class_matrix.sql desde CSV
   - Implementar bacteria_profile_generator.py con acumulación
   - Validar con queries SQL

**¿Procedo con actualización del backlog principal y generación de migraciones?**
