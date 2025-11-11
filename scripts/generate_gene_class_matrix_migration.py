"""
Script para generar migración SQL desde matriz gen × clase.
Genera: src/migrations/016_seed_gene_class_matrix.sql

Autor: GitHub Copilot + JhoneiroLove
Fecha: 10 de noviembre de 2025
"""

import csv
from pathlib import Path
from collections import defaultdict

# Rutas
PROJECT_ROOT = Path(__file__).parent.parent
MATRIZ_CSV = (
    PROJECT_ROOT
    / "docs"
    / "matriz_genes_x_clases_MIC_multiplicadores_LONG_utf8_bom.csv"
)
OUTPUT_SQL = PROJECT_ROOT / "src" / "migrations" / "016_seed_gene_class_matrix.sql"

# Mapeo clase → antibióticos
ANTIBIOTIC_CLASS_MAP = {
    "carbapenemicos": ["Meropenem", "Imipenem", "Doripenem"],
    "cef_3G_ceftazidima": ["Ceftazidima"],
    "cef_4G_cefepime": ["Cefepime"],
    "cef_inhibidor": ["Ceftazidima/Avibactam", "Ceftolozano/Tazobactam"],
    "monobactam_aztreonam": ["Aztreonam"],
    "penicilina_inhibidor": ["Piperacilina/Tazobactam"],
    "aminoglucosidos": ["Amikacina", "Tobramicina"],
    "fluoroquinolonas": ["Ciprofloxacino", "Levofloxacino"],
    "polimixinas": ["Colistina"],
    "sideroforo_cefiderocol": ["Cefiderocol"],
}


def parse_matrix():
    """Parse matriz CSV y retorna lista de multiplicadores."""
    multipliers = []
    genes_seen = set()
    clases_seen = set()

    with open(MATRIZ_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mult = {
                "gen": row["gen"].strip(),
                "clase": row["clase"].strip(),
                "multiplicador": float(row["multiplicador_MIC"]),
            }
            multipliers.append(mult)
            genes_seen.add(mult["gen"])
            clases_seen.add(mult["clase"])

    return multipliers, sorted(genes_seen), sorted(clases_seen)


def generate_sql(multipliers, genes, clases):
    """Genera contenido SQL desde matriz."""
    sql_lines = []

    # Header
    sql_lines.append(
        "-- Migración 016: Seed de Matriz Gen × Clase (Multiplicadores MIC)"
    )
    sql_lines.append("-- Fecha de generación: 10 de noviembre de 2025")
    sql_lines.append(
        "-- Fuente: matriz_genes_x_clases_MIC_multiplicadores_LONG_utf8_bom.csv"
    )
    sql_lines.append("-- Referencias: CARD, ResFinder, NCBI AMR, publicaciones PMID")
    sql_lines.append("")
    sql_lines.append(f"-- Genes documentados ({len(genes)}):")
    for gene in genes:
        sql_lines.append(f"--   • {gene}")
    sql_lines.append("")
    sql_lines.append(f"-- Clases de antibióticos ({len(clases)}):")
    for clase in clases:
        antibiotics = ANTIBIOTIC_CLASS_MAP.get(clase, [])
        ab_list = ", ".join(antibiotics) if antibiotics else "Sin antibióticos mapeados"
        sql_lines.append(f"--   • {clase}: {ab_list}")
    sql_lines.append("")

    # Tabla gene_class_multipliers
    sql_lines.append("-- ============================================")
    sql_lines.append("-- TABLA: gene_class_multipliers")
    sql_lines.append("-- ============================================")
    sql_lines.append("")
    sql_lines.append("CREATE TABLE IF NOT EXISTS gene_class_multipliers (")
    sql_lines.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
    sql_lines.append(
        "    gen TEXT NOT NULL,                      -- Nombre del gen mutado"
    )
    sql_lines.append(
        "    clase_antibiotica TEXT NOT NULL,        -- Clase de antibiótico afectada"
    )
    sql_lines.append(
        "    multiplicador_mic REAL NOT NULL,        -- Factor de incremento MIC (1.0 = sin efecto)"
    )
    sql_lines.append("    UNIQUE(gen, clase_antibiotica)")
    sql_lines.append(");")
    sql_lines.append("")

    # INSERTs agrupados por clase
    sql_lines.append("-- ============================================")
    sql_lines.append("-- MULTIPLICADORES POR CLASE")
    sql_lines.append("-- ============================================")
    sql_lines.append("")

    # Agrupar por clase
    by_class = defaultdict(list)
    for mult in multipliers:
        by_class[mult["clase"]].append(mult)

    for clase in sorted(by_class.keys()):
        class_mults = by_class[clase]
        antibiotics = ANTIBIOTIC_CLASS_MAP.get(clase, [])
        ab_str = ", ".join(antibiotics) if antibiotics else "N/A"

        sql_lines.append(f"-- Clase: {clase} ({ab_str})")

        # Filtrar multiplicadores > 1.0 (efectos relevantes)
        relevant_mults = [m for m in class_mults if m["multiplicador"] > 1.0]
        if relevant_mults:
            sql_lines.append(
                f"-- Genes con efecto (multiplicador > 1.0): {len(relevant_mults)}"
            )
            for m in relevant_mults:
                sql_lines.append(f"--   {m['gen']}: ×{m['multiplicador']}")
        else:
            sql_lines.append("-- (Sin genes con efecto significativo en esta clase)")

        sql_lines.append("")

        # INSERTs para esta clase
        for mult in class_mults:
            sql_lines.append(
                f"INSERT INTO gene_class_multipliers (gen, clase_antibiotica, multiplicador_mic) VALUES\n"
                f"('{mult['gen']}', '{mult['clase']}', {mult['multiplicador']});"
            )

        sql_lines.append("")

    # Tabla antibiotic_classes
    sql_lines.append("-- ============================================")
    sql_lines.append("-- TABLA: antibiotic_classes (Mapeo)")
    sql_lines.append("-- ============================================")
    sql_lines.append("")
    sql_lines.append("CREATE TABLE IF NOT EXISTS antibiotic_classes (")
    sql_lines.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
    sql_lines.append("    antibiotico TEXT NOT NULL,")
    sql_lines.append(
        "    clase TEXT NOT NULL,                     -- FK a gene_class_multipliers.clase_antibiotica"
    )
    sql_lines.append("    UNIQUE(antibiotico)")
    sql_lines.append(");")
    sql_lines.append("")

    # INSERTs para mapeo
    sql_lines.append("-- Mapeo Antibiótico → Clase")
    sql_lines.append("")
    for clase, antibiotics in sorted(ANTIBIOTIC_CLASS_MAP.items()):
        for ab in antibiotics:
            sql_lines.append(
                f"INSERT INTO antibiotic_classes (antibiotico, clase) VALUES\n"
                f"('{ab}', '{clase}');"
            )

    sql_lines.append("")

    # Validaciones
    sql_lines.append("-- ============================================")
    sql_lines.append("-- VALIDACIÓN CIENTÍFICA")
    sql_lines.append("-- ============================================")
    sql_lines.append("")
    sql_lines.append("-- 1. Verificar total de combinaciones gen × clase")
    sql_lines.append("-- SELECT COUNT(*) FROM gene_class_multipliers;")
    sql_lines.append(f"-- Debe retornar: {len(multipliers)}")
    sql_lines.append("")
    sql_lines.append("-- 2. Genes críticos en carbapenem (alta resistencia)")
    sql_lines.append("-- SELECT gen, multiplicador_mic FROM gene_class_multipliers")
    sql_lines.append(
        "-- WHERE clase_antibiotico='carbapenemicos' AND multiplicador_mic > 1"
    )
    sql_lines.append("-- ORDER BY multiplicador_mic DESC;")
    sql_lines.append(
        "-- Debe retornar: blaVIM_or_blaIMP (16.0), oprD_loss (8.0), ftsI_PBP3_insertion_YRIN (2.0)"
    )
    sql_lines.append("")
    sql_lines.append("-- 3. Genes críticos en fluoroquinolonas")
    sql_lines.append("-- SELECT gen, multiplicador_mic FROM gene_class_multipliers")
    sql_lines.append(
        "-- WHERE clase_antibiotico='fluoroquinolonas' AND multiplicador_mic > 1"
    )
    sql_lines.append("-- ORDER BY multiplicador_mic DESC;")
    sql_lines.append(
        "-- Debe retornar: gyrA_T83I (8.0), parC_S87L (4.0), mexR_frameshift (4.0), nalC_Q83K (2.0)"
    )
    sql_lines.append("")
    sql_lines.append("-- 4. Verificar mapeo antibióticos → clases")
    sql_lines.append(
        "-- SELECT antibiotico, clase FROM antibiotic_classes ORDER BY clase, antibiotico;"
    )
    sql_lines.append(
        f"-- Debe retornar: {sum(len(abs) for abs in ANTIBIOTIC_CLASS_MAP.values())} filas"
    )
    sql_lines.append("")
    sql_lines.append(
        "-- 5. Ejemplo de cálculo MIC con acumulación (oprD_loss + blaVIM en Meropenem)"
    )
    sql_lines.append("-- SELECT g.gen, g.multiplicador_mic")
    sql_lines.append("-- FROM gene_class_multipliers g")
    sql_lines.append("-- JOIN antibiotic_classes a ON a.clase = g.clase_antibiotico")
    sql_lines.append(
        "-- WHERE a.antibiotico = 'Meropenem' AND g.gen IN ('oprD_loss', 'blaVIM_or_blaIMP');"
    )
    sql_lines.append("-- Debe retornar: oprD_loss (8.0), blaVIM_or_blaIMP (16.0)")
    sql_lines.append("-- Cálculo: MIC_base (0.5) × 8 × 16 = 64 µg/mL (Resistente)")

    return "\n".join(sql_lines)


def main():
    print("Generando migracion 016_seed_gene_class_matrix.sql...")
    print(f"Matriz CSV: {MATRIZ_CSV}")
    print()

    # Parse matriz
    print("Parseando matriz gen x clase...")
    multipliers, genes, clases = parse_matrix()
    print(f"  {len(genes)} genes documentados")
    print(f"  {len(clases)} clases de antibioticos")
    print(f"  {len(multipliers)} combinaciones gen x clase")
    print()

    # Estadisticas de impacto
    print("Analisis de impacto:")
    relevant_mults = [m for m in multipliers if m["multiplicador"] > 1.0]
    print(f"  - Multiplicadores con efecto (>1.0): {len(relevant_mults)}")
    print(
        f"  - Multiplicadores sin efecto (=1.0): {len(multipliers) - len(relevant_mults)}"
    )

    max_mult = max(m["multiplicador"] for m in multipliers)
    max_entry = next(m for m in multipliers if m["multiplicador"] == max_mult)
    print(
        f"  - Multiplicador maximo: {max_entry['gen']} x {max_entry['clase']} = x{max_mult}"
    )
    print()

    # Generar SQL
    print("Generando SQL...")
    sql_content = generate_sql(multipliers, genes, clases)

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
    print(
        "  2. Verificar multiplicadores criticos (blaVIM x carbapenem=16, gyrA x FQ=8)"
    )
    print("  3. Validar mapeo antibiotico -> clase es correcto")
    print("  4. Ejecutar queries de validacion al final del archivo")
    print()
    print("Listo para revision cientifica.")


if __name__ == "__main__":
    main()
