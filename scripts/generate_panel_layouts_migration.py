"""
Script para generar migracion SQL de panel layouts (96 wells).
Genera: src/migrations/017_seed_panel_layouts.sql

Autor: GitHub Copilot + JhoneiroLove
Fecha: 11 de noviembre de 2025
"""

import csv
from pathlib import Path
from collections import defaultdict

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
CONCENTRACIONES_CSV = (
    PROJECT_ROOT / "docs" / "pseudomonas_aeruginosa_concentraciones_simuladas.csv"
)
OUTPUT_SQL = PROJECT_ROOT / "src" / "migrations" / "017_seed_panel_layouts.sql"

# Configuracion panel 96 wells
ROWS = ["A", "B", "C", "D", "E", "F", "G", "H"]
COLS = list(range(1, 13))  # 1-12
QC_WELLS = {"H11": "control_positivo", "H12": "control_negativo"}


def parse_concentraciones():
    """Parse CSV de concentraciones y retorna lista de antibioticos con rangos."""
    antibioticos = []

    with open(CONCENTRACIONES_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["Antibiotico"].strip():
                continue

            ab = {
                "nombre": row["Antibiotico"].strip(),
                "min": float(row["Rango_Min"]),
                "max": float(row["Rango_Max"]),
                "paso": row["Paso"].strip(),
                "fuente": row["Fuente"].strip(),
            }

            # Generar serie log2
            concentraciones = []
            current = ab["min"]
            while current <= ab["max"]:
                concentraciones.append(current)
                current *= 2

            ab["concentraciones"] = concentraciones
            antibioticos.append(ab)

    return antibioticos


def assign_wells(antibioticos):
    """Asigna antibioticos y concentraciones a wells del panel 96."""
    wells = []

    # Ordenar por numero de concentraciones (descendente)
    antibioticos_sorted = sorted(
        antibioticos, key=lambda x: len(x["concentraciones"]), reverse=True
    )

    current_row = 0
    current_col = 0
    well_count = 0
    max_test_wells = 94  # 96 - 2 QC

    for ab in antibioticos_sorted:
        for conc in ab["concentraciones"]:
            if well_count >= max_test_wells:
                break

            row = ROWS[current_row]
            col = COLS[current_col]
            well_position = f"{row}{col}"

            # Saltar H11 y H12
            if well_position in QC_WELLS:
                current_col += 1
                if current_col >= 12:
                    current_col = 0
                    current_row += 1
                row = ROWS[current_row]
                col = COLS[current_col]
                well_position = f"{row}{col}"

            wells.append(
                {
                    "position": well_position,
                    "antibiotico": ab["nombre"],
                    "concentracion": conc,
                    "tipo": "test",
                    "panel_name": "EUCAST_PA_Standard",
                }
            )

            well_count += 1

            # Avanzar
            current_col += 1
            if current_col >= 12:
                current_col = 0
                current_row += 1
                if current_row > 7:
                    break

    # Agregar QC
    for well_pos, control_type in QC_WELLS.items():
        wells.append(
            {
                "position": well_pos,
                "antibiotico": None,
                "concentracion": None,
                "tipo": control_type,
                "panel_name": "EUCAST_PA_Standard",
            }
        )

    return wells


def generate_sql(wells, antibioticos):
    """Genera contenido SQL desde wells asignados."""
    sql_lines = []

    sql_lines.append("-- Migracion 017: Seed de Panel Layouts (96 Wells)")
    sql_lines.append("-- Fecha de generacion: 11 de noviembre de 2025")
    sql_lines.append("-- Fuente: pseudomonas_aeruginosa_concentraciones_simuladas.csv")
    sql_lines.append("")
    sql_lines.append(f"-- Total wells: {len(wells)}")
    sql_lines.append("")

    sql_lines.append("CREATE TABLE IF NOT EXISTS panel_layouts (")
    sql_lines.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
    sql_lines.append("    panel_name TEXT NOT NULL,")
    sql_lines.append("    well_position TEXT NOT NULL,")
    sql_lines.append("    antibiotico TEXT,")
    sql_lines.append("    concentracion REAL,")
    sql_lines.append("    tipo TEXT NOT NULL,")
    sql_lines.append("    UNIQUE(panel_name, well_position)")
    sql_lines.append(");")
    sql_lines.append("")

    by_antibiotic = defaultdict(list)
    qc_wells = []

    for well in wells:
        if well["tipo"] == "test":
            by_antibiotic[well["antibiotico"]].append(well)
        else:
            qc_wells.append(well)

    for ab_name in sorted(by_antibiotic.keys()):
        ab_wells = by_antibiotic[ab_name]
        concs = [w["concentracion"] for w in ab_wells]

        sql_lines.append(
            f"-- {ab_name} ({len(ab_wells)} wells): {min(concs)}-{max(concs)} ug/mL"
        )

        for well in ab_wells:
            sql_lines.append(
                f"INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', '{well['position']}', "
                f"'{well['antibiotico']}', {well['concentracion']}, 'test');"
            )

        sql_lines.append("")

    sql_lines.append("-- Controles QC")
    for well in qc_wells:
        sql_lines.append(
            f"INSERT INTO panel_layouts VALUES (NULL, 'EUCAST_PA_Standard', '{well['position']}', "
            f"NULL, NULL, '{well['tipo']}');"
        )

    return "\n".join(sql_lines)


def main():
    print("Generando migracion 017_seed_panel_layouts.sql...")

    antibioticos = parse_concentraciones()
    total_diluciones = sum(len(ab["concentraciones"]) for ab in antibioticos)
    print(f"  {len(antibioticos)} antibioticos, {total_diluciones} diluciones")

    wells = assign_wells(antibioticos)
    test_count = len([w for w in wells if w["tipo"] == "test"])
    print(f"  {test_count} wells test, 2 QC, {len(wells)} total")

    sql_content = generate_sql(wells, antibioticos)

    OUTPUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write(sql_content)

    print(f"Migracion generada: {OUTPUT_SQL} ({len(sql_content)} caracteres)")
    print("Listo para revision.")


if __name__ == "__main__":
    main()
