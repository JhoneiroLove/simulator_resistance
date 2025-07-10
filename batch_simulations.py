#!/usr/bin/env python3
"""
Script para ejecutar 385 simulaciones con parámetros aleatorios
Cada simulación tendrá 100 generaciones con combinaciones aleatorias de parámetros
"""

import os
import sys
import random
import logging
import time
from itertools import combinations
from datetime import datetime

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.data.database import init_db, get_session
from src.data.models import Gen, Antibiotico, Simulacion
from src.core.genetic_algorithm import GeneticAlgorithm
from src.core.reporting import save_simulation_report, save_generation_metrics
from src.utils.logging_config import setup_logging


class BatchSimulationRunner:
    def __init__(self):
        # Configurar logging
        setup_logging()
        self.logger = logging.getLogger(__name__)

        # Inicializar BD
        init_db()

        # Cargar datos de la BD
        self.load_database_data()

        # Parámetros de configuración para simulaciones
        self.setup_parameter_ranges()

    def load_database_data(self):
        """Carga genes y antibióticos desde la base de datos"""
        session = get_session()

        # Cargar genes
        genes_orm = session.query(Gen).all()
        self.genes = [
            {"id": g.id, "nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_orm
        ]

        # Cargar antibióticos
        antibiotics_orm = session.query(Antibiotico).all()
        self.antibiotics = [
            {
                "id": ab.id,
                "nombre": ab.nombre,
                "tipo": ab.tipo,
                "concentracion_minima": ab.concentracion_minima,
                "concentracion_maxima": ab.concentracion_maxima,
            }
            for ab in antibiotics_orm
        ]

        session.close()

        self.logger.info(
            f"Cargados {len(self.genes)} genes y {len(self.antibiotics)} antibióticos"
        )

    def setup_parameter_ranges(self):
        """Define los rangos de parámetros para generar combinaciones aleatorias"""

        # Rangos de parámetros principales (ignorando parámetros avanzados)
        self.param_ranges = {
            "mutation_rate": (0.05, 1.0),  # Desde input_form.py
            "death_rate": (0.03, 1.0),  # Desde input_form.py
            "reproduction_rate": (0.01, 5.0),  # Desde input_form.py
            "temperature": (25.0, 45.0),  # Desde input_form.py
            "pH": (5.0, 9.0),  # Desde input_form.py
            "pop_size": (50, 300),  # Rango razonable para tamaño población
        }

        # Configuración para selección de genes (entre 2 y 8 genes por simulación)
        self.min_genes = 2
        self.max_genes = min(8, len(self.genes))

        # Configuración para horarios de antibióticos (1-4 eventos por simulación)
        self.min_antibiotic_events = 1
        self.max_antibiotic_events = 4

    def generate_random_parameters(self):
        """Genera un conjunto aleatorio de parámetros para una simulación"""

        params = {}

        # Generar parámetros numéricos aleatorios
        for param_name, (min_val, max_val) in self.param_ranges.items():
            params[param_name] = random.uniform(min_val, max_val)

        # Selección aleatoria de genes (2-8 genes)
        num_genes = random.randint(self.min_genes, self.max_genes)
        selected_genes = random.sample([g["id"] for g in self.genes], num_genes)
        params["selected_genes"] = selected_genes

        # Factores ambientales
        params["environmental_factors"] = {
            "temperature": params["temperature"],
            "pH": params["pH"],
        }

        # Generar horario de antibióticos aleatorio
        params["antibiotic_schedule"] = self.generate_random_antibiotic_schedule()

        return params

    def generate_random_antibiotic_schedule(self):
        """Genera un horario aleatorio de aplicación de antibióticos"""

        num_events = random.randint(
            self.min_antibiotic_events, self.max_antibiotic_events
        )
        schedule = []

        # Generar tiempos aleatorios entre 0 y 90 (para que haya margen hasta generación 100)
        times = sorted(random.sample(range(0, 91), num_events))

        for time_point in times:
            # Seleccionar antibiótico aleatorio
            antibiotic = random.choice(self.antibiotics)

            # Generar concentración aleatoria dentro del rango del antibiótico
            concentration = random.uniform(
                antibiotic["concentracion_minima"], antibiotic["concentracion_maxima"]
            )

            schedule.append((time_point, antibiotic, concentration))

        return schedule

    def run_single_simulation(self, sim_number, params):
        """Ejecuta una sola simulación con los parámetros dados"""

        start_time = time.time()

        try:
            # Crear registro de simulación en BD
            session = get_session()

            # Usar el primer antibiótico del horario para el registro principal
            first_antibiotic = (
                params["antibiotic_schedule"][0][1]
                if params["antibiotic_schedule"]
                else None
            )
            first_concentration = (
                params["antibiotic_schedule"][0][2]
                if params["antibiotic_schedule"]
                else 0.0
            )

            simulacion = Simulacion(
                antibiotico_id=first_antibiotic["id"] if first_antibiotic else None,
                concentracion=first_concentration,
                resistencia_predicha=0.0,  # Se actualizará al final
            )
            session.add(simulacion)
            session.commit()
            simulation_id = simulacion.id
            session.close()

            # Crear algoritmo genético con parámetros aleatorios
            ga = GeneticAlgorithm(
                genes=self.genes,
                antibiotic_schedule=params["antibiotic_schedule"],
                mutation_rate=params["mutation_rate"],
                generations=100,  # Fijo en 100 como se requiere
                pop_size=int(params["pop_size"]),
                death_rate=params["death_rate"],
                environmental_factors=params["environmental_factors"],
                simulation_id=simulation_id,
                reproduction_rate=params["reproduction_rate"],
            )

            # Inicializar y ejecutar simulación
            ga.initialize(params["selected_genes"])

            # Ejecutar todas las generaciones
            for generation in range(100):
                if not ga.step():
                    break

                # Log de progreso cada 25 generaciones
                if generation % 25 == 0:
                    self.logger.info(f"Sim {sim_number}/385 - Gen {generation}/100")

            # Guardar atributos finales
            ga.save_final_gene_attributes(params["selected_genes"])

            # Actualizar resistencia predicha en BD
            final_resistance = ga.avg_hist[-1] if ga.avg_hist else 0.0
            session = get_session()
            simulacion = session.query(Simulacion).get(simulation_id)
            simulacion.resistencia_predicha = final_resistance
            session.commit()
            session.close()

            # Guardar reportes
            saved_params = {
                "genes": params["selected_genes"],
                "mutation_rate": params["mutation_rate"],
                "death_rate": params["death_rate"],
                "generations": 100,
                "environmental_factors": params["environmental_factors"],
                "reproduction_rate": params["reproduction_rate"],
                "pop_size": int(params["pop_size"]),
            }

            save_simulation_report(ga, saved_params)
            save_generation_metrics(ga, simulation_id)

            elapsed_time = time.time() - start_time

            self.logger.info(
                f"Simulación {sim_number}/385 completada - "
                f"Resistencia final: {final_resistance:.4f} - "
                f"Tiempo: {elapsed_time:.2f}s"
            )

            return {
                "simulation_id": simulation_id,
                "final_resistance": final_resistance,
                "execution_time": elapsed_time,
                "success": True,
            }

        except Exception as e:
            self.logger.error(f"Error en simulación {sim_number}: {str(e)}")
            return {
                "simulation_id": None,
                "final_resistance": None,
                "execution_time": time.time() - start_time,
                "success": False,
                "error": str(e),
            }

    def run_batch_simulations(self):
        """Ejecuta las 385 simulaciones completas"""

        self.logger.info("Iniciando batch de 385 simulaciones...")
        start_time = time.time()

        results = []
        successful_sims = 0
        failed_sims = 0

        for sim_num in range(1, 386):  # 1 a 385
            self.logger.info(f"\n=== INICIANDO SIMULACIÓN {sim_num}/385 ===")

            # Generar parámetros aleatorios para esta simulación
            params = self.generate_random_parameters()

            # Log de parámetros clave
            self.logger.info(f"Genes seleccionados: {len(params['selected_genes'])}")
            self.logger.info(
                f"Eventos antibióticos: {len(params['antibiotic_schedule'])}"
            )
            self.logger.info(f"Tasa mutación: {params['mutation_rate']:.3f}")
            self.logger.info(f"Tasa mortalidad: {params['death_rate']:.3f}")

            # Ejecutar simulación
            result = self.run_single_simulation(sim_num, params)
            results.append(result)

            if result["success"]:
                successful_sims += 1
            else:
                failed_sims += 1

            # Log de progreso general cada 25 simulaciones
            if sim_num % 25 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / sim_num
                estimated_remaining = avg_time * (385 - sim_num)

                self.logger.info(
                    f"\n=== PROGRESO: {sim_num}/385 simulaciones ===\n"
                    f"Exitosas: {successful_sims}, Fallidas: {failed_sims}\n"
                    f"Tiempo transcurrido: {elapsed / 60:.1f} min\n"
                    f"Tiempo estimado restante: {estimated_remaining / 60:.1f} min\n"
                )

        # Resumen final
        total_time = time.time() - start_time
        self.logger.info(
            f"\n=== BATCH COMPLETADO ===\n"
            f"Total simulaciones: 385\n"
            f"Exitosas: {successful_sims}\n"
            f"Fallidas: {failed_sims}\n"
            f"Tiempo total: {total_time / 60:.2f} minutos\n"
            f"Tiempo promedio por simulación: {total_time / 385:.2f} segundos"
        )

        return results


def main():
    """Función principal del script"""

    print("=== SCRIPT DE BATCH DE 385 SIMULACIONES ===")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Cada simulación tendrá 100 generaciones con parámetros aleatorios\n")

    try:
        # Crear y ejecutar el runner
        runner = BatchSimulationRunner()
        results = runner.run_batch_simulations()

        # Análisis básico de resultados
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            resistances = [r["final_resistance"] for r in successful_results]
            times = [r["execution_time"] for r in successful_results]

            print(f"\n=== ANÁLISIS DE RESULTADOS ===")
            print(f"Resistencia promedio: {sum(resistances) / len(resistances):.4f}")
            print(f"Resistencia mínima: {min(resistances):.4f}")
            print(f"Resistencia máxima: {max(resistances):.4f}")
            print(f"Tiempo promedio por simulación: {sum(times) / len(times):.2f}s")

        print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("¡Batch de simulaciones completado!")

    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario. Saliendo...")
        sys.exit(1)
    except Exception as e:
        print(f"\nError crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
