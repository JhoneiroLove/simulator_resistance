import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

class CSVValidator:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.engine = create_engine("sqlite:///resistencia.db")

    def compare_with_simulations(self):
        """Compara datos históricos con simulaciones almacenadas en la BD."""
        try:
            # Leer CSV histórico
            df_historico = pd.read_csv(self.csv_path)
            required_columns = ["Antibiotico", "Resistencia_Observada"]
            if not all(col in df_historico.columns for col in required_columns):
                raise ValueError(
                    "CSV debe contener columnas: 'Antibiotico', 'Resistencia_Observada'"
                )

            # Leer simulaciones de la BD
            query = """
                SELECT 
                    a.nombre AS antibiotico,
                    s.resistencia_predicha,
                    s.fecha
                FROM simulaciones s
                JOIN antibioticos a ON s.antibiotico_id = a.id
            """
            df_simulaciones = pd.read_sql(query, self.engine)

            # Unir datasets
            merged = pd.merge(
                df_historico,
                df_simulaciones,
                left_on="Antibiotico",
                right_on="antibiotico",
                how="inner",
            )

            # Calcular métricas
            merged["Diferencia_Absoluta"] = abs(
                merged["Resistencia_Observada"] - merged["resistencia_predicha"]
            )
            merged["Error_Relativo"] = (
                merged["Diferencia_Absoluta"] / merged["Resistencia_Observada"]
            ) * 100

            return merged[
                [
                    "Antibiotico",
                    "Resistencia_Observada",
                    "resistencia_predicha",
                    "Diferencia_Absoluta",
                    "Error_Relativo",
                ]
            ]

        except SQLAlchemyError as e:
            raise Exception(f"Error de base de datos: {str(e)}")
        except Exception as e:
            raise Exception(f"Error general: {str(e)}")