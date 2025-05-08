from src.data.database import get_session
from src.data.models import Gen, Antibiotico

def insert_test_data():
    session = get_session()  # Ahora funciona correctamente

    # Limpiar tablas existentes (opcional)
    session.query(Gen).delete()
    session.query(Antibiotico).delete()

    # Genes de prueba
    genes = [
        Gen(
            nombre="blaVIM",
            peso_resistencia=0.6,
            descripcion="Carbapenemasa de tipo VIM",
        ),
        Gen(nombre="mexAB-oprM", peso_resistencia=0.4, descripcion="Bomba de eflujo"),
    ]

    # Antibióticos de prueba
    antibioticos = [
        Antibiotico(
            nombre="Meropenem",
            concentracion_minima=0.1,
            concentracion_maxima=1000,
            tipo="Carbapenémico",
        ),
        Antibiotico(
            nombre="Ciprofloxacino",
            concentracion_minima=0.05,
            concentracion_maxima=500,
            tipo="Fluoroquinolona",
        ),
    ]

    try:
        session.add_all(genes + antibioticos)
        session.commit()
        print("✅ Datos de prueba insertados correctamente.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    insert_test_data()