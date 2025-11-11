-- Migracion 018: Actualizacion tabla antibioticos (familias y mecanismos)
-- Fecha de generacion: 11 de noviembre de 2025
-- Fuente: familias_antibioticas_y_especies_base_utf8_bom.csv

-- Antibioticos a actualizar: 13

-- ============================================
-- MODIFICAR ESTRUCTURA DE TABLA
-- ============================================

-- Agregar columnas para metadata educativa
ALTER TABLE antibioticos ADD COLUMN familia TEXT;
ALTER TABLE antibioticos ADD COLUMN mecanismo_accion TEXT;

-- ============================================
-- ACTUALIZAR METADATA POR ANTIBIOTICO
-- ============================================

-- Meropenem (Carbapenémico)
UPDATE antibioticos SET familia='Carbapenémico', mecanismo_accion='Inhibe la síntesis de pared bacteriana' WHERE nombre='Meropenem';

-- Imipenem (Carbapenémico)
UPDATE antibioticos SET familia='Carbapenémico', mecanismo_accion='Inhibe la síntesis de pared bacteriana' WHERE nombre='Imipenem';

-- Cefepime (Cefalosporina (4ta gen))
UPDATE antibioticos SET familia='Cefalosporina (4ta gen)', mecanismo_accion='Inhibe síntesis de peptidoglucano' WHERE nombre='Cefepime';

-- Ceftazidima (Cefalosporina (3ra gen))
UPDATE antibioticos SET familia='Cefalosporina (3ra gen)', mecanismo_accion='Interfiere en la pared celular bacteriana' WHERE nombre='Ceftazidima';

-- Amikacina (Aminoglucósido)
UPDATE antibioticos SET familia='Aminoglucósido', mecanismo_accion='Inhibe síntesis proteica (30S ribosomal)' WHERE nombre='Amikacina';

-- Tobramicina (Aminoglucósido)
UPDATE antibioticos SET familia='Aminoglucósido', mecanismo_accion='Inhibe síntesis proteica' WHERE nombre='Tobramicina';

-- Ciprofloxacino (Fluoroquinolona)
UPDATE antibioticos SET familia='Fluoroquinolona', mecanismo_accion='Inhibe ADN girasa y topoisomerasa IV' WHERE nombre='Ciprofloxacino';

-- Levofloxacino (Fluoroquinolona)
UPDATE antibioticos SET familia='Fluoroquinolona', mecanismo_accion='Inhibe replicación del ADN bacteriano' WHERE nombre='Levofloxacino';

-- Colistina (Polimixina)
UPDATE antibioticos SET familia='Polimixina', mecanismo_accion='Altera la membrana externa bacteriana' WHERE nombre='Colistina';

-- Piperacilina/Tazobactam (β-lactámico + inhibidor β-lactamasa)
UPDATE antibioticos SET familia='β-lactámico + inhibidor β-lactamasa', mecanismo_accion='Inhibe síntesis de pared y bloquea β-lactamasas' WHERE nombre='Piperacilina/Tazobactam';

-- Ceftazidima/Avibactam (Cefalosporina + inhibidor β-lactamasa)
UPDATE antibioticos SET familia='Cefalosporina + inhibidor β-lactamasa', mecanismo_accion='Bloquea β-lactamasas clase A y C' WHERE nombre='Ceftazidima/Avibactam';

-- Ceftolozano/Tazobactam (Cefalosporina + inhibidor β-lactamasa)
UPDATE antibioticos SET familia='Cefalosporina + inhibidor β-lactamasa', mecanismo_accion='Alta afinidad por PBPs, estable ante AmpC' WHERE nombre='Ceftolozano/Tazobactam';

-- Cefiderocol (Cefalosporina sideróforo)
UPDATE antibioticos SET familia='Cefalosporina sideróforo', mecanismo_accion='Usa transporte dependiente de hierro' WHERE nombre='Cefiderocol';

-- ============================================
-- VALIDACION
-- ============================================

-- 1. Verificar antibioticos actualizados
-- SELECT nombre, familia, mecanismo_accion FROM antibioticos
-- WHERE familia IS NOT NULL
-- ORDER BY familia, nombre;
-- Debe retornar: 13 filas

-- 2. Verificar familias unicas
-- SELECT DISTINCT familia FROM antibioticos
-- WHERE familia IS NOT NULL
-- ORDER BY familia;
-- Debe retornar: 9 familias

-- 3. Listar antibioticos sin metadata (si existen)
-- SELECT nombre FROM antibioticos WHERE familia IS NULL;
-- Debe retornar: 0 filas (todos actualizados)