"""
Script para generar migracion SQL de actualizacion de tabla antibioticos.
Genera: src/migrations/018_update_antibioticos_familias.sql

Autor: GitHub Copilot + JhoneiroLove
Fecha: 11 de noviembre de 2025
"""

import csv
from pathlib import Path

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
FAMILIAS_CSV = (
    PROJECT_ROOT / "docs" / "familias_antibioticas_y_especies_base_utf8_bom.csv"
)
OUTPUT_SQL = (
    PROJECT_ROOT / "src" / "migrations" / "018_update_antibioticos_familias.sql"
)


def parse_familias():
    """Parse CSV de familias y retorna lista de antibioticos con metadata."""
    antibioticos = []

    with open(FAMILIAS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row["Antibiótico"].strip():
                continue

            antibioticos.append(
                {
                    "nombre": row["Antibiótico"].strip(),
                    "familia": row["Familia"].strip(),
                    "mecanismo": row["Mecanismo_de_acción"].strip(),
                    "especies": row["Especies_aplicables"].strip(),
                    "fuente": row["Fuente"].strip(),
                }
            )

    return antibioticos


def generate_sql(antibioticos):
    """Genera contenido SQL de migracion ALTER TABLE + UPDATE."""
    sql_lines = []

    # Header
    sql_lines.append(
        "-- Migracion 018: Actualizacion tabla antibioticos (familias y mecanismos)"
    )
    sql_lines.append("-- Fecha de generacion: 11 de noviembre de 2025")
    sql_lines.append("-- Fuente: familias_antibioticas_y_especies_base_utf8_bom.csv")
    sql_lines.append("")
    sql_lines.append(f"-- Antibioticos a actualizar: {len(antibioticos)}")
    sql_lines.append("")

    # ALTER TABLE
    sql_lines.append("-- ============================================")
    sql_lines.append("-- MODIFICAR ESTRUCTURA DE TABLA")
    sql_lines.append("-- ============================================")
    sql_lines.append("")
    sql_lines.append("-- Agregar columnas para metadata educativa")
    sql_lines.append("ALTER TABLE antibioticos ADD COLUMN familia TEXT;")
    sql_lines.append("ALTER TABLE antibioticos ADD COLUMN mecanismo_accion TEXT;")
    sql_lines.append("")

    # UPDATEs
    sql_lines.append("-- ============================================")
    sql_lines.append("-- ACTUALIZAR METADATA POR ANTIBIOTICO")
    sql_lines.append("-- ============================================")
    sql_lines.append("")

    for ab in antibioticos:
        sql_lines.append(f"-- {ab['nombre']} ({ab['familia']})")
        sql_lines.append(
            f"UPDATE antibioticos SET "
            f"familia='{ab['familia']}', "
            f"mecanismo_accion='{ab['mecanismo']}' "
            f"WHERE nombre='{ab['nombre']}';"
        )
        sql_lines.append("")

    # Validaciones
    sql_lines.append("-- ============================================")
    sql_lines.append("-- VALIDACION")
    sql_lines.append("-- ============================================")
    sql_lines.append("")
    sql_lines.append("-- 1. Verificar antibioticos actualizados")
    sql_lines.append("-- SELECT nombre, familia, mecanismo_accion FROM antibioticos")
    sql_lines.append("-- WHERE familia IS NOT NULL")
    sql_lines.append("-- ORDER BY familia, nombre;")
    sql_lines.append(f"-- Debe retornar: {len(antibioticos)} filas")
    sql_lines.append("")
    sql_lines.append("-- 2. Verificar familias unicas")
    sql_lines.append("-- SELECT DISTINCT familia FROM antibioticos")
    sql_lines.append("-- WHERE familia IS NOT NULL")
    sql_lines.append("-- ORDER BY familia;")

    # Contar familias unicas
    familias_unicas = set(ab["familia"] for ab in antibioticos)
    sql_lines.append(f"-- Debe retornar: {len(familias_unicas)} familias")
    sql_lines.append("")
    sql_lines.append("-- 3. Listar antibioticos sin metadata (si existen)")
    sql_lines.append("-- SELECT nombre FROM antibioticos WHERE familia IS NULL;")
    sql_lines.append("-- Debe retornar: 0 filas (todos actualizados)")

    return "\n".join(sql_lines)


def main():
    print("Generando migracion 018_update_antibioticos_familias.sql...")
    print(f"CSV: {FAMILIAS_CSV}")
    print()

    antibioticos = parse_familias()
    print(f"  {len(antibioticos)} antibioticos")

    familias = set(ab["familia"] for ab in antibioticos)
    print(f"  {len(familias)} familias unicas:")
    for familia in sorted(familias):
        count = len([ab for ab in antibioticos if ab["familia"] == familia])
        print(f"    - {familia}: {count} antibioticos")
    print()

    sql_content = generate_sql(antibioticos)

    OUTPUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write(sql_content)

    print(f"Migracion generada: {OUTPUT_SQL}")
    print(f"Tamano: {len(sql_content)} caracteres")
    print()
    print("Listo para revision.")


if __name__ == "__main__":
    main()
