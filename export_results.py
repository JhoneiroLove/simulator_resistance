#!/usr/bin/env python3
"""
Script para exportar resultados de simulaciones desde la BD a Excel/CSV
Organiza los datos por indicadores en diferentes hojas/archivos
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.data.database import init_db, get_session
from src.data.models import (
    Simulacion,
    SimulacionAtributos,
    ReporteSimulacion,
    MetricaGeneracion,
    Gen,
    Antibiotico,
)
from src.utils.logging_config import setup_logging


class ResultsExporter:
    def __init__(self, output_format="excel"):
        """
        Inicializa el exportador de resultados

        Args:
            output_format (str): 'excel' para generar un archivo .xlsx con múltiples hojas
                               'csv' para generar múltiples archivos .csv
        """
        setup_logging()
        init_db()
        self.output_format = output_format.lower()
        self.session = get_session()

        # Crear directorio de salida
        self.output_dir = "exported_results"
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"Iniciando exportación en formato: {self.output_format}")
        print(f"Directorio de salida: {self.output_dir}")

    def get_simulation_summary(self):
        """Obtiene un resumen general de todas las simulaciones"""

        query = """
        SELECT 
            s.id as simulacion_id,
            s.fecha as fecha_simulacion,
            s.resistencia_predicha,
            ab.nombre as antibiotico_nombre,
            ab.tipo as antibiotico_tipo,
            s.concentracion,
            rs.generaciones_totales,
            rs.parametros_input
        FROM simulaciones s
        LEFT JOIN antibioticos ab ON s.antibiotico_id = ab.id  
        LEFT JOIN reportes_simulacion rs ON s.id = rs.simulacion_id
        ORDER BY s.id
        """

        df = pd.read_sql_query(query, self.session.bind)

        # Parsear parámetros JSON para expandir columnas
        if "parametros_input" in df.columns:
            params_expanded = []
            for _, row in df.iterrows():
                params = {}
                if row["parametros_input"]:
                    try:
                        params = json.loads(row["parametros_input"])
                    except:
                        pass

                # Expandir parámetros principales
                params_row = {
                    "mutation_rate": params.get("mutation_rate", None),
                    "death_rate": params.get("death_rate", None),
                    "reproduction_rate": params.get("reproduction_rate", None),
                    "pop_size": params.get("pop_size", None),
                    "temperature": params.get("environmental_factors", {}).get(
                        "temperature", None
                    ),
                    "pH": params.get("environmental_factors", {}).get("pH", None),
                    "num_genes_selected": len(params.get("genes", []))
                    if params.get("genes")
                    else None,
                }
                params_expanded.append(params_row)

            # Agregar columnas de parámetros al DataFrame
            params_df = pd.DataFrame(params_expanded)
            df = pd.concat([df, params_df], axis=1)

            # Eliminar la columna JSON original
            df = df.drop("parametros_input", axis=1)

        return df

    def get_all_metrics_by_indicator(self):
        """Obtiene todas las métricas organizadas por indicador"""

        indicators = [
            "avg_fitness",
            "best_fitness",
            "diversidad_genetica",
            "tasa_mutacion",
            "tasa_convergencia",
            "cpu_time_sec",
            "ram_mb",
        ]

        metrics_data = {}

        for indicator in indicators:
            query = f"""
            SELECT 
                mg.simulacion_id,
                mg.generacion,
                mg.valor as {indicator}
            FROM metricas_generacion mg
            WHERE mg.nombre_indicador = '{indicator}'
            ORDER BY mg.simulacion_id, mg.generacion
            """

            df = pd.read_sql_query(query, self.session.bind)
            if not df.empty:
                metrics_data[indicator] = df

        return metrics_data

    def get_metrics_summary_by_simulation(self):
        """Obtiene un resumen de métricas finales por simulación"""

        query = """
        SELECT 
            mg.simulacion_id,
            MAX(CASE WHEN mg.nombre_indicador = 'avg_fitness' THEN mg.valor END) as avg_fitness_final,
            MAX(CASE WHEN mg.nombre_indicador = 'best_fitness' THEN mg.valor END) as best_fitness_final,
            MAX(CASE WHEN mg.nombre_indicador = 'diversidad_genetica' THEN mg.valor END) as diversidad_genetica_final,
            MAX(CASE WHEN mg.nombre_indicador = 'tasa_mutacion' THEN mg.valor END) as tasa_mutacion_final,
            MAX(CASE WHEN mg.nombre_indicador = 'tasa_convergencia' THEN mg.valor END) as tasa_convergencia_final,
            MAX(CASE WHEN mg.nombre_indicador = 'cpu_time_sec' THEN mg.valor END) as cpu_time_total,
            MAX(CASE WHEN mg.nombre_indicador = 'ram_mb' THEN mg.valor END) as ram_mb_max
        FROM metricas_generacion mg
        WHERE mg.generacion = (
            SELECT MAX(mg2.generacion) 
            FROM metricas_generacion mg2 
            WHERE mg2.simulacion_id = mg.simulacion_id
        )
        GROUP BY mg.simulacion_id
        ORDER BY mg.simulacion_id
        """

        return pd.read_sql_query(query, self.session.bind)

    def get_biological_attributes(self):
        """Obtiene la evolución de atributos biológicos"""

        query = """
        SELECT 
            sa.simulacion_id,
            sa.generacion,
            sa.atributo,
            sa.valor_promedio,
            sa.desviacion_std,
            ab.nombre as antibiotico_aplicado,
            ab.tipo as tipo_antibiotico
        FROM simulacion_atributos sa
        LEFT JOIN antibioticos ab ON sa.antibiotico_id = ab.id
        WHERE sa.atributo IN ('recubrimiento', 'reproduccion', 'letalidad', 'permeabilidad', 'enzimas')
        ORDER BY sa.simulacion_id, sa.generacion, sa.atributo
        """

        return pd.read_sql_query(query, self.session.bind)

    def get_gene_expression(self):
        """Obtiene la expresión final de genes por simulación"""

        query = """
        SELECT 
            sa.simulacion_id,
            sa.atributo,
            sa.valor_promedio,
            sa.desviacion_std,
            REPLACE(sa.atributo, 'gen_', '') as gen_nombre
        FROM simulacion_atributos sa
        WHERE sa.atributo LIKE 'gen_%'
        ORDER BY sa.simulacion_id, sa.atributo
        """

        return pd.read_sql_query(query, self.session.bind)

    def get_resistance_analysis(self):
        """Análisis de resistencia: correlaciones entre parámetros y resistencia final"""

        # Primero obtenemos el resumen
        summary_df = self.get_simulation_summary()

        if summary_df.empty:
            return pd.DataFrame()

        # Calcular estadísticas de resistencia por grupos
        resistance_stats = []

        # Por tipo de antibiótico
        if "antibiotico_tipo" in summary_df.columns:
            by_antibiotic = (
                summary_df.groupby("antibiotico_tipo")["resistencia_predicha"]
                .agg(["count", "mean", "std", "min", "max"])
                .reset_index()
            )
            by_antibiotic["categoria"] = "Tipo_Antibiotico"
            by_antibiotic = by_antibiotic.rename(columns={"antibiotico_tipo": "valor"})
            resistance_stats.append(by_antibiotic)

        # Por rangos de temperatura
        if "temperature" in summary_df.columns:
            summary_df["temp_range"] = pd.cut(
                summary_df["temperature"],
                bins=[0, 30, 35, 40, 50],
                labels=["Baja(<30)", "Normal(30-35)", "Alta(35-40)", "Crítica(>40)"],
            )
            by_temp = (
                summary_df.groupby("temp_range")["resistencia_predicha"]
                .agg(["count", "mean", "std", "min", "max"])
                .reset_index()
            )
            by_temp["categoria"] = "Rango_Temperatura"
            by_temp = by_temp.rename(columns={"temp_range": "valor"})
            resistance_stats.append(by_temp)

        # Por rangos de pH
        if "pH" in summary_df.columns:
            summary_df["ph_range"] = pd.cut(
                summary_df["pH"],
                bins=[0, 6.5, 7.5, 9],
                labels=["Ácido(<6.5)", "Neutro(6.5-7.5)", "Básico(>7.5)"],
            )
            by_ph = (
                summary_df.groupby("ph_range")["resistencia_predicha"]
                .agg(["count", "mean", "std", "min", "max"])
                .reset_index()
            )
            by_ph["categoria"] = "Rango_pH"
            by_ph = by_ph.rename(columns={"ph_range": "valor"})
            resistance_stats.append(by_ph)

        if resistance_stats:
            return pd.concat(resistance_stats, ignore_index=True)
        else:
            return pd.DataFrame()

    def get_convergence_analysis(self):
        """Análisis de convergencia: simulaciones que convergieron vs no convergieron"""

        # Obtener la tasa de convergencia final de cada simulación
        query = """
        SELECT 
            mg.simulacion_id,
            MAX(mg.generacion) as generacion_final,
            AVG(CASE WHEN mg.nombre_indicador = 'tasa_convergencia' THEN mg.valor END) as tasa_convergencia_final,
            AVG(CASE WHEN mg.nombre_indicador = 'diversidad_genetica' THEN mg.valor END) as diversidad_final
        FROM metricas_generacion mg
        WHERE mg.generacion = (
            SELECT MAX(mg2.generacion) 
            FROM metricas_generacion mg2 
            WHERE mg2.simulacion_id = mg.simulacion_id
        )
        AND mg.nombre_indicador IN ('tasa_convergencia', 'diversidad_genetica')
        GROUP BY mg.simulacion_id
        ORDER BY mg.simulacion_id
        """

        convergence_df = pd.read_sql_query(query, self.session.bind)

        if not convergence_df.empty:
            # Clasificar convergencia
            convergence_df["convergencia_estado"] = pd.cut(
                convergence_df["tasa_convergencia_final"],
                bins=[0, 0.001, 0.01, float("inf")],
                labels=["Convergió", "Convergencia_Lenta", "No_Convergió"],
            )

            # Clasificar diversidad
            convergence_df["diversidad_estado"] = pd.cut(
                convergence_df["diversidad_final"],
                bins=[0, 1.5, 3.0, float("inf")],
                labels=["Baja", "Moderada", "Alta"],
            )

        return convergence_df

    def export_to_excel(self):
        """Exporta todos los datos a un archivo Excel con múltiples hojas"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/resultados_simulaciones_{timestamp}.xlsx"

        print(f"Exportando a Excel: {filename}")

        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
            # 1. Resumen General
            print("Exportando resumen general...")
            summary_df = self.get_simulation_summary()
            if not summary_df.empty:
                summary_df.to_excel(writer, sheet_name="1_Resumen_General", index=False)

            # 2. Resumen de Métricas Finales por Simulación
            print("Exportando resumen de métricas finales...")
            metrics_summary_df = self.get_metrics_summary_by_simulation()
            if not metrics_summary_df.empty:
                metrics_summary_df.to_excel(
                    writer, sheet_name="2_Metricas_Finales", index=False
                )

            # 3-9. Cada Indicador en su Propia Hoja
            print("Exportando métricas por indicador...")
            all_metrics = self.get_all_metrics_by_indicator()

            indicator_sheets = {
                "avg_fitness": "3_Avg_Fitness",
                "best_fitness": "4_Best_Fitness",
                "diversidad_genetica": "5_Diversidad_Genetica",
                "tasa_mutacion": "6_Tasa_Mutacion",
                "tasa_convergencia": "7_Tasa_Convergencia",
                "cpu_time_sec": "8_CPU_Time",
                "ram_mb": "9_RAM_Usage",
            }

            for indicator, sheet_name in indicator_sheets.items():
                if indicator in all_metrics and not all_metrics[indicator].empty:
                    print(f"  Exportando {indicator}...")
                    all_metrics[indicator].to_excel(
                        writer, sheet_name=sheet_name, index=False
                    )

            # 10. Atributos Biológicos
            print("Exportando atributos biológicos...")
            bio_df = self.get_biological_attributes()
            if not bio_df.empty:
                bio_df.to_excel(
                    writer, sheet_name="10_Biological_Attributes", index=False
                )

            # 11. Expresión de Genes
            print("Exportando expresión de genes...")
            genes_df = self.get_gene_expression()
            if not genes_df.empty:
                genes_df.to_excel(writer, sheet_name="11_Gene_Expression", index=False)

            # 12. Análisis de Resistencia
            print("Exportando análisis de resistencia...")
            resistance_df = self.get_resistance_analysis()
            if not resistance_df.empty:
                resistance_df.to_excel(
                    writer, sheet_name="12_Resistance_Analysis", index=False
                )

        return filename

    def export_to_csv(self):
        """Exporta cada indicador a un archivo CSV separado"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_dir = f"{self.output_dir}/csv_export_{timestamp}"
        os.makedirs(csv_dir, exist_ok=True)

        print(f"Exportando a CSV en directorio: {csv_dir}")

        exported_files = []

        # 1. Resumen General
        print("Exportando resumen general...")
        summary_df = self.get_simulation_summary()
        if not summary_df.empty:
            filename = f"{csv_dir}/1_resumen_general.csv"
            summary_df.to_csv(filename, index=False, encoding="utf-8-sig")
            exported_files.append(filename)

        # 2. Resumen de Métricas Finales
        print("Exportando resumen de métricas finales...")
        metrics_summary_df = self.get_metrics_summary_by_simulation()
        if not metrics_summary_df.empty:
            filename = f"{csv_dir}/2_metricas_finales.csv"
            metrics_summary_df.to_csv(filename, index=False, encoding="utf-8-sig")
            exported_files.append(filename)

        # 3-9. Cada Indicador por Separado
        print("Exportando métricas por indicador...")
        all_metrics = self.get_all_metrics_by_indicator()

        indicator_files = {
            "avg_fitness": "3_avg_fitness.csv",
            "best_fitness": "4_best_fitness.csv",
            "diversidad_genetica": "5_diversidad_genetica.csv",
            "tasa_mutacion": "6_tasa_mutacion.csv",
            "tasa_convergencia": "7_tasa_convergencia.csv",
            "cpu_time_sec": "8_cpu_time.csv",
            "ram_mb": "9_ram_usage.csv",
        }

        for indicator, csv_filename in indicator_files.items():
            if indicator in all_metrics and not all_metrics[indicator].empty:
                print(f"  Exportando {indicator}...")
                filename = f"{csv_dir}/{csv_filename}"
                all_metrics[indicator].to_csv(
                    filename, index=False, encoding="utf-8-sig"
                )
                exported_files.append(filename)

        # 10. Atributos Biológicos
        print("Exportando atributos biológicos...")
        bio_df = self.get_biological_attributes()
        if not bio_df.empty:
            filename = f"{csv_dir}/10_biological_attributes.csv"
            bio_df.to_csv(filename, index=False, encoding="utf-8-sig")
            exported_files.append(filename)

        # 11. Expresión de Genes
        print("Exportando expresión de genes...")
        genes_df = self.get_gene_expression()
        if not genes_df.empty:
            filename = f"{csv_dir}/11_gene_expression.csv"
            genes_df.to_csv(filename, index=False, encoding="utf-8-sig")
            exported_files.append(filename)

        # 12. Análisis de Resistencia
        print("Exportando análisis de resistencia...")
        resistance_df = self.get_resistance_analysis()
        if not resistance_df.empty:
            filename = f"{csv_dir}/12_resistance_analysis.csv"
            resistance_df.to_csv(filename, index=False, encoding="utf-8-sig")
            exported_files.append(filename)

        return exported_files

    def generate_export_summary(self, exported_file_or_files):
        """Genera un resumen de la exportación realizada"""

        total_simulations = self.session.query(Simulacion).count()
        total_metrics = self.session.query(MetricaGeneracion).count()
        total_attributes = self.session.query(SimulacionAtributos).count()

        summary = f"""
=== RESUMEN DE EXPORTACIÓN ===
Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Formato: {self.output_format.upper()}

DATOS EXPORTADOS:
- Total de simulaciones: {total_simulations}
- Total de métricas por generación: {total_metrics}
- Total de atributos biológicos: {total_attributes}

HOJAS/ARCHIVOS GENERADOS:
1. Resumen General - Parámetros y resultados finales de cada simulación
2. Métricas Finales - Valores finales de todos los indicadores por simulación

INDICADORES ESPECÍFICOS (uno por hoja/archivo):
3. Avg Fitness - Fitness promedio por generación y simulación
4. Best Fitness - Mejor fitness por generación y simulación  
5. Diversidad Genética - Diversidad por generación y simulación
6. Tasa Mutación - Tasa de mutación por generación y simulación
7. Tasa Convergencia - Tasa de convergencia por generación y simulación
8. CPU Time - Tiempo de CPU acumulado por generación y simulación
9. RAM Usage - Uso de memoria RAM por generación y simulación

DATOS ADICIONALES:
10. Biological Attributes - Evolución de atributos biológicos
11. Gene Expression - Expresión final de genes de resistencia
12. Resistance Analysis - Análisis estadístico de resistencia por categorías

"""

        if self.output_format == "excel":
            summary += f"ARCHIVO GENERADO:\n{exported_file_or_files}\n"
        else:
            summary += f"ARCHIVOS GENERADOS:\n"
            for file in exported_file_or_files:
                summary += f"- {file}\n"

        print(summary)

        # Guardar resumen en archivo de texto
        summary_file = f"{self.output_dir}/export_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        return summary_file

    def export_results(self):
        """Método principal para exportar resultados"""

        try:
            if self.output_format == "excel":
                exported = self.export_to_excel()
                print(f"\n✅ Exportación exitosa a Excel: {exported}")
            elif self.output_format == "csv":
                exported = self.export_to_csv()
                print(
                    f"\n✅ Exportación exitosa a CSV: {len(exported)} archivos generados"
                )
            else:
                raise ValueError(f"Formato no soportado: {self.output_format}")

            # Generar resumen
            summary_file = self.generate_export_summary(exported)
            print(f"\n📄 Resumen guardado en: {summary_file}")

            return exported

        except Exception as e:
            print(f"\n❌ Error durante la exportación: {e}")
            raise
        finally:
            self.session.close()


def main():
    """Función principal del script"""

    print("=== EXPORTADOR DE RESULTADOS DE SIMULACIONES ===")
    print("Este script exporta los resultados de las simulaciones desde la BD")
    print("Organiza los datos por indicadores en diferentes hojas/archivos\n")

    # Solicitar formato de exportación
    while True:
        format_choice = (
            input("¿Qué formato prefieres? [excel/csv] (excel): ").strip().lower()
        )
        if format_choice == "" or format_choice == "excel":
            output_format = "excel"
            break
        elif format_choice == "csv":
            output_format = "csv"
            break
        else:
            print("Por favor, elige 'excel' o 'csv'")

    try:
        # Crear exportador y ejecutar
        exporter = ResultsExporter(output_format=output_format)
        exported = exporter.export_results()

        print(f"\n🎉 ¡Exportación completada exitosamente!")
        print(f"Revisa el directorio: exported_results/")

    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
