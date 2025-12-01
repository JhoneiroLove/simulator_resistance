"""
Script para inicializar la base de datos desde cero
Aplica todas las migraciones en orden
"""

import os
import sys

# Agregar el directorio raíz al path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.data.database import init_db, get_session, db_path
from sqlalchemy import text

print("=" * 60)
print("🔄 INICIALIZACIÓN DE BASE DE DATOS")
print("=" * 60)

# Verificar si la BD existe
if os.path.exists(db_path):
    print(f"\n⚠️  Base de datos existente encontrada: {db_path}")
    print(f"   Tamaño: {os.path.getsize(db_path)} bytes")
    response = input("\n¿Deseas eliminarla y crear una nueva? (s/n): ")
    if response.lower() == "s":
        os.remove(db_path)
        print("✅ Base de datos eliminada.")
    else:
        print("❌ Operación cancelada.")
        sys.exit(0)
else:
    print(f"\n📁 Se creará nueva base de datos en: {db_path}")

print("\n" + "=" * 60)
print("🚀 Aplicando migraciones...")
print("=" * 60 + "\n")

# Ejecutar init_db que aplica todas las migraciones
try:
    init_db()

    # RNF-5: Optimizar índices para queries frecuentes
    print("\n🔧 Optimizando índices de base de datos...")
    from src.utils.green_optimization import QueryOptimizer
    from src.data.models import BacteriaProfile, PanelLayout

    session = get_session()
    QueryOptimizer.add_indexes(session, BacteriaProfile, ["id", "organismo"])
    QueryOptimizer.add_indexes(session, PanelLayout, ["id", "panel_name"])
    session.close()
    print("✅ Índices optimizados")

    print("\n" + "=" * 60)
    print("✅ Base de datos inicializada correctamente")
    print("=" * 60)

    # Verificar datos cargados
    print("\n📊 VERIFICANDO DATOS CIENTÍFICOS CARGADOS:\n")
    session = get_session()

    tables_to_check = [
        ("breakpoints", "Breakpoints CLSI/EUCAST"),
        ("gene_class_multipliers", "Multiplicadores MIC"),
        ("panel_layouts", "Layouts de paneles AST"),
        ("antibiotic_classes", "Clases de antibióticos"),
        ("bacteria_profiles", "Perfiles bacterianos"),
    ]

    for table_name, description in tables_to_check:
        try:
            count = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            status = "✅" if count > 0 else "⚠️"
            print(f"{status} {description:.<40} {count:>5} registros")
        except Exception as e:
            print(f"❌ {description:.<40} Error: {str(e)[:30]}")

    session.close()

    print("\n" + "=" * 60)
    print("🎉 Proceso completado exitosamente")
    print("=" * 60)
    print(f"\n📍 Base de datos lista en: {db_path}")

except Exception as e:
    print("\n" + "=" * 60)
    print(f"❌ ERROR DURANTE LA INICIALIZACIÓN")
    print("=" * 60)
    print(f"\n{str(e)}\n")
    sys.exit(1)
