import sys

sys.path.insert(0, ".")
from src.data.database import get_session
from sqlalchemy import text

session = get_session()
tables = session.execute(
    text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
).fetchall()

print("=" * 60)
print("TABLAS EN LA BASE DE DATOS ACTUAL:")
print("=" * 60)
for table in tables:
    count = session.execute(text(f"SELECT COUNT(*) FROM {table[0]}")).scalar()
    print(f"✅ {table[0]:<30} {count:>5} registros")

session.close()
