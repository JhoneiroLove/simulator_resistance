import csv
import math

with open(
    "docs/pseudomonas_aeruginosa_concentraciones_simuladas.csv", encoding="utf-8-sig"
) as f:
    reader = csv.DictReader(f)
    total = 0
    for row in reader:
        if not row["Antibiotico"].strip():
            continue
        min_val = float(row["Rango_Min"])
        max_val = float(row["Rango_Max"])
        num_diluciones = int(math.log2(max_val / min_val)) + 1
        print(f"{row['Antibiotico'].strip()}: {num_diluciones} diluciones")
        total += num_diluciones

    print(f"\nTotal: {total} diluciones")
    print(f"Wells disponibles: 84 (7 filas x 12 columnas)")
    print(f"Deficit: {total - 84} wells")
