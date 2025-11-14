import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.genotype_phenotype_calculator import GenotypePhenotypeCalculator

calc = GenotypePhenotypeCalculator()
mults = calc.load_multipliers_from_db()

print("Antibióticos en cache:", len(mults))
if "Meropenem" in mults:
    print("\nMeropenem genes:", list(mults["Meropenem"].keys()))
else:
    print("\n❌ Meropenem NO está en cache")
    print("Antibióticos disponibles:", list(mults.keys()))
