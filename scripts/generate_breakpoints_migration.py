"""
Script para generar migración SQL desde CSV de breakpoints EUCAST/CLSI.
Genera: src/migrations/015_seed_breakpoints.sql

Autor: GitHub Copilot + JhoneiroLove
Fecha: 10 de noviembre de 2025
"""

import csv
import os
from pathlib import Path

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
EUCAST_CSV = PROJECT_ROOT / "docs" / "eucast_pseudomonas_aeruginosa_v15_2025.csv"
CLSI_CSV = (
    PROJECT_ROOT / "docs" / "pseudomonas_aeruginosa_clsi_breakpoints_extracted.csv"
)
FAMILIAS_CSV = (
    PROJECT_ROOT / "docs" / "familias_antibioticas_y_especies_base_utf8_bom.csv"
)
OUTPUT_SQL = PROJECT_ROOT / "src" / "migrations" / "015_seed_breakpoints.sql"


def load_familias():
    """Carga mapeo antibiotico -> familia/mecanismo desde CSV."""
    familias_map = {}
    with open(FAMILIAS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            antibiotico = row["Antibiótico"].strip()
            familias_map[antibiotico] = {
                "familia": row["Familia"].strip(),
                "mecanismo": row["Mecanismo_de_acción"].strip(),
            }
    return familias_map


def normalize_antibiotic_name(name):
    """Normaliza nombres de antibióticos para matching."""
    # Mapeo de variaciones conocidas
    mappings = {
        "Piperacilina/Tazobactam": "Piperacillin-Tazobactam",
        "Ticarcilina/Clavulanato": "Ticarcillin-Clavulanate",
        "Ceftazidima/Avibactam": "Ceftazidime-Avibactam",
        "Ceftolozano/Tazobactam": "Ceftolozane-Tazobactam",
        "Meropenem/Vaborbactam": "Meropenem-Vaborbactam",
        "Ciprofloxacino": "Ciprofloxacin",
        "Levofloxacino": "Levofloxacin",
        "Amikacina": "Amikacin",
        "Tobramicina": "Tobramycin",
        "Colistina": "Colistin",
        "Ceftazidima": "Ceftazidime",
        "Piperacilina": "Piperacillin",
    }
    return mappings.get(name, name)


def parse_eucast():
    """Parse EUCAST CSV y retorna lista de breakpoints."""
    breakpoints = []
    familias = load_familias()

    with open(EUCAST_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            antibiotico = row["Antibiotico"].strip()

            # Buscar familia/mecanismo
            familia_info = familias.get(
                antibiotico, {"familia": None, "mecanismo": None}
            )

            bp = {
                "antibiotico": antibiotico,
                "organismo": "Pseudomonas aeruginosa",
                "s_mic": float(row["S_MIC"]),
                "r_mic": float(row["R_MIC"]),
                "standard": "EUCAST",
                "fuente": row["Fuente"].strip(),
                "familia": familia_info["familia"],
                "mecanismo": familia_info["mecanismo"],
            }
            breakpoints.append(bp)

    return breakpoints


def parse_clsi_fallbacks(eucast_antibiotics):
    """Parse CLSI CSV solo para antibióticos NO en EUCAST."""
    breakpoints = []
    familias = load_familias()

    with open(CLSI_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            antibiotico = row["Antibiotic"].strip()

            # Normalizar nombre para comparación
            normalized = normalize_antibiotic_name(antibiotico)

            # Skip si ya está en EUCAST
            if any(
                normalize_antibiotic_name(ab) == normalized for ab in eucast_antibiotics
            ):
                continue

            # Skip si no tiene breakpoints definidos
            s_mic = row["S_MIC"].strip()
            r_mic = row["R_MIC"].strip()
            if s_mic == "-" or r_mic == "-" or not s_mic or not r_mic:
                continue

            # Buscar familia
            familia_info = familias.get(
                antibiotico, {"familia": "Desconocida", "mecanismo": None}
            )

            bp = {
                "antibiotico": antibiotico,
                "organismo": "Pseudomonas aeruginosa",
                "s_mic": float(s_mic)
                if "/" not in s_mic
                else None,  # Skip combinaciones
                "r_mic": float(r_mic) if "/" not in r_mic else None,
                "standard": "CLSI",
                "fuente": row["Fuente"].strip(),
                "familia": familia_info["familia"],
                "mecanismo": familia_info["mecanismo"],
            }

            # Solo agregar si parseó correctamente
            if bp["s_mic"] is not None and bp["r_mic"] is not None:
                breakpoints.append(bp)

    return breakpoints


def generate_sql(breakpoints):
    """Genera contenido SQL desde lista de breakpoints."""
    sql_lines = []

    # Header
    sql_lines.append("-- Migración 015: Seed de Breakpoints (EUCAST v15.0 + CLSI M07)")
    sql_lines.append("-- Fecha de generación: 10 de noviembre de 2025")
    sql_lines.append("-- Fuentes: EUCAST v_15.0_Breakpoint_Tables.pdf, CLSI M07 (2023)")
    sql_lines.append("-- Organismo: Pseudomonas aeruginosa (hardcoded)")
    sql_lines.append("")

    # Crear tabla
    sql_lines.append("CREATE TABLE IF NOT EXISTS breakpoints (")
    sql_lines.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
    sql_lines.append("    antibiotico TEXT NOT NULL,")
    sql_lines.append("    organismo TEXT NOT NULL DEFAULT 'Pseudomonas aeruginosa',")
    sql_lines.append(
        "    s_mic REAL NOT NULL,       -- Susceptible si MIC ≤ este valor"
    )
    sql_lines.append("    r_mic REAL NOT NULL,       -- Resistente si MIC > este valor")
    sql_lines.append("    standard TEXT NOT NULL,    -- 'EUCAST' o 'CLSI'")
    sql_lines.append("    fuente TEXT NOT NULL,      -- Referencia oficial")
    sql_lines.append("    familia TEXT,              -- Familia antibiótica")
    sql_lines.append("    mecanismo TEXT,            -- Mecanismo de acción")
    sql_lines.append("    UNIQUE(antibiotico, standard)")
    sql_lines.append(");")
    sql_lines.append("")

    # INSERTs por estándar
    sql_lines.append("-- ============================================")
    sql_lines.append("-- BREAKPOINTS EUCAST v15.0 (2025) - PRIMARIOS")
    sql_lines.append("-- ============================================")
    sql_lines.append("")

    eucast_bps = [bp for bp in breakpoints if bp["standard"] == "EUCAST"]
    for bp in eucast_bps:
        familia = f"'{bp['familia']}'" if bp["familia"] else "NULL"
        mecanismo = f"'{bp['mecanismo']}'" if bp["mecanismo"] else "NULL"

        sql_lines.append(
            f"INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES\n"
            f"('{bp['antibiotico']}', '{bp['organismo']}', {bp['s_mic']}, {bp['r_mic']}, "
            f"'{bp['standard']}', '{bp['fuente']}', {familia}, {mecanismo});"
        )

    sql_lines.append("")
    sql_lines.append("-- ============================================")
    sql_lines.append("-- BREAKPOINTS CLSI M07 (2023) - FALLBACKS")
    sql_lines.append("-- ============================================")
    sql_lines.append("")

    clsi_bps = [bp for bp in breakpoints if bp["standard"] == "CLSI"]
    for bp in clsi_bps:
        familia = f"'{bp['familia']}'" if bp["familia"] else "NULL"
        mecanismo = f"'{bp['mecanismo']}'" if bp["mecanismo"] else "NULL"

        sql_lines.append(
            f"INSERT INTO breakpoints (antibiotico, organismo, s_mic, r_mic, standard, fuente, familia, mecanismo) VALUES\n"
            f"('{bp['antibiotico']}', '{bp['organismo']}', {bp['s_mic']}, {bp['r_mic']}, "
            f"'{bp['standard']}', '{bp['fuente']}', {familia}, {mecanismo});"
        )

    sql_lines.append("")
    sql_lines.append("-- ============================================")
    sql_lines.append("-- VALIDACIÓN")
    sql_lines.append("-- ============================================")
    sql_lines.append("-- Verificar total de breakpoints cargados")
    sql_lines.append(
        "-- SELECT COUNT(*) FROM breakpoints WHERE organismo='Pseudomonas aeruginosa';"
    )
    sql_lines.append(f"-- Debe retornar: {len(breakpoints)}")
    sql_lines.append("")
    sql_lines.append("-- Verificar breakpoints EUCAST (primarios)")
    sql_lines.append(
        "-- SELECT antibiotico, s_mic, r_mic FROM breakpoints WHERE standard='EUCAST' ORDER BY antibiotico;"
    )
    sql_lines.append(f"-- Debe retornar: {len(eucast_bps)} filas")
    sql_lines.append("")
    sql_lines.append("-- Verificar breakpoints CLSI (fallbacks)")
    sql_lines.append(
        "-- SELECT antibiotico FROM breakpoints WHERE standard='CLSI' ORDER BY antibiotico;"
    )
    sql_lines.append(f"-- Debe retornar: {len(clsi_bps)} filas")

    return "\n".join(sql_lines)


def main():
    print("🔬 Generando migración 015_seed_breakpoints.sql...")
    print(f"📂 EUCAST CSV: {EUCAST_CSV}")
    print(f"📂 CLSI CSV: {CLSI_CSV}")
    print(f"Familias CSV: {FAMILIAS_CSV}")
    print()

    # Parse EUCAST (primarios)
    print("Parseando EUCAST v15.0...")
    eucast_breakpoints = parse_eucast()
    print(f"  {len(eucast_breakpoints)} antibioticos EUCAST")

    # Parse CLSI (fallbacks)
    print("Parseando CLSI M07 (solo fallbacks)...")
    eucast_antibiotics = [bp["antibiotico"] for bp in eucast_breakpoints]
    clsi_fallbacks = parse_clsi_fallbacks(eucast_antibiotics)
    print(f"  {len(clsi_fallbacks)} antibioticos CLSI adicionales")

    # Combinar
    all_breakpoints = eucast_breakpoints + clsi_fallbacks
    print(f"Total breakpoints: {len(all_breakpoints)}")
    print()

    # Generar SQL
    print("Generando SQL...")
    sql_content = generate_sql(all_breakpoints)

    # Crear directorio si no existe
    OUTPUT_SQL.parent.mkdir(parents=True, exist_ok=True)

    # Escribir archivo
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write(sql_content)

    print(f"Migracion generada: {OUTPUT_SQL}")
    print(f"Tamano: {len(sql_content)} caracteres")
    print()
    print("REVISION MANUAL REQUERIDA:")
    print("  1. Abrir archivo SQL generado")
    print("  2. Verificar valores S_MIC y R_MIC son correctos")
    print("  3. Validar familias/mecanismos asignados")
    print("  4. Ejecutar queries de validacion al final del archivo")
    print()
    print("Listo para revision.")


if __name__ == "__main__":
    main()
