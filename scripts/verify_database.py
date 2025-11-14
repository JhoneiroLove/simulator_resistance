"""Verificar datos en base de datos"""

from src.data.database import get_session
from sqlalchemy import text

session = get_session()

tables = [
    ("genes", "Genes de resistencia"),
    ("antibioticos", "Antibióticos"),
    ("breakpoints", "Breakpoints CLSI/EUCAST"),
    ("gene_class_multipliers", "Multiplicadores MIC"),
    ("panel_layouts", "Paneles AST"),
    ("antibiotic_classes", "Clases de antibióticos"),
]

print("\n📊 DATOS EN BASE DE DATOS:\n")
for table, desc in tables:
    try:
        count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"✅ {desc:.<40} {count:>5} registros")
    except Exception as e:
        print(f"❌ {desc:.<40} Error")

session.close()
print("\n✅ Base de datos lista para usar\n")
