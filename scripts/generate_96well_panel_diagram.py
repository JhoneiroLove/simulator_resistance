"""
Generador de diagrama visual de panel AST de 96 pozos.

Este script genera una representación gráfica del layout de un panel de
susceptibilidad antimicrobiana (AST) en formato de microplaca de 96 pozos.

Muestra:
- Distribución de antibióticos y concentraciones
- Código de colores por familia antibiótica
- Pocillos de control (positivo/negativo)
- Gradientes de concentración (diluciones seriadas)

Autor: Sistema AST Simulator
Fecha: 2 de diciembre de 2025
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np
from typing import List, Dict, Tuple
import sys
import os

# Agregar path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.database import get_session
from src.data.models import PanelLayout


# Paleta de colores por familia antibiótica
ANTIBIOTIC_COLORS = {
    "β-lactámicos": "#FF6B6B",  # Rojo
    "Carbapenémicos": "#4ECDC4",  # Turquesa
    "Fluoroquinolonas": "#45B7D1",  # Azul
    "Aminoglicósidos": "#96CEB4",  # Verde
    "Polimixinas": "#FFEAA7",  # Amarillo
    "Control Positivo": "#FFFFFF",  # Blanco
    "Control Negativo": "#2D3436",  # Negro
    "Otro": "#DFE6E9",  # Gris claro
}

# Mapeo antibiótico → familia
ANTIBIOTIC_FAMILIES = {
    "piperacillin_tazobactam": "β-lactámicos",
    "ceftazidime": "β-lactámicos",
    "cefepime": "β-lactámicos",
    "aztreonam": "β-lactámicos",
    "imipenem": "Carbapenémicos",
    "meropenem": "Carbapenémicos",
    "doripenem": "Carbapenémicos",
    "ciprofloxacin": "Fluoroquinolonas",
    "levofloxacin": "Fluoroquinolonas",
    "gentamicin": "Aminoglicósidos",
    "tobramycin": "Aminoglicósidos",
    "amikacin": "Aminoglicósidos",
    "colistin": "Polimixinas",
    "positive_control": "Control Positivo",
    "negative_control": "Control Negativo",
}


def well_to_row_col(well_position: str) -> Tuple[int, int]:
    """
    Convierte posición de well (ej: 'A1') a coordenadas (row, col).

    Args:
        well_position: Posición en formato 'A1', 'B12', etc.

    Returns:
        Tupla (row, col) con índices 0-based
    """
    row = ord(well_position[0].upper()) - ord("A")
    col = int(well_position[1:]) - 1
    return row, col


def get_family(antibiotic: str) -> str:
    """Obtiene familia antibiótica para un antibiótico."""
    if not antibiotic:
        return "Otro"
    return ANTIBIOTIC_FAMILIES.get(antibiotic.lower(), "Otro")


def load_panel_layout(panel_name: str = "EUCAST_Pseudomonas") -> List[Dict]:
    """
    Carga layout de panel desde la base de datos.

    Args:
        panel_name: Nombre del panel a cargar

    Returns:
        Lista de dicts con estructura de wells
    """
    session = get_session()

    records = (
        session.query(PanelLayout).filter(PanelLayout.panel_name == panel_name).all()
    )

    session.close()

    if not records:
        print(f"⚠️  Panel '{panel_name}' no encontrado en BD")
        return []

    wells = []
    for record in records:
        wells.append(
            {
                "position": record.well_position,
                "antibiotic": record.antibiotico,
                "concentration": record.concentracion,
                "type": record.tipo,
                "family": get_family(record.antibiotico),
            }
        )

    return wells


def generate_96well_diagram(
    panel_name: str = "EUCAST_Pseudomonas", save_path: str = None
):
    """
    Genera diagrama visual de panel AST de 96 pozos.

    Args:
        panel_name: Nombre del panel a visualizar
        save_path: Ruta para guardar la imagen (opcional)
    """
    print(f"🔬 Generando diagrama de panel: {panel_name}")

    # Cargar datos del panel
    wells = load_panel_layout(panel_name)

    if not wells:
        print("❌ No se pudo generar el diagrama (panel vacío)")
        return

    # Crear figura
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor("white")

    # Configurar ejes
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 8.5)
    ax.set_aspect("equal")
    ax.invert_yaxis()  # Invertir Y para que A esté arriba

    # Etiquetas de columnas (1-12)
    ax.set_xticks(range(12))
    ax.set_xticklabels([str(i + 1) for i in range(12)], fontsize=10, fontweight="bold")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")

    # Etiquetas de filas (A-H)
    ax.set_yticks(range(8))
    ax.set_yticklabels(
        ["A", "B", "C", "D", "E", "F", "G", "H"], fontsize=10, fontweight="bold"
    )

    # Eliminar bordes
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Dibujar wells
    for well in wells:
        row, col = well_to_row_col(well["position"])
        family = well["family"]
        color = ANTIBIOTIC_COLORS.get(family, ANTIBIOTIC_COLORS["Otro"])

        # Dibujar círculo del well
        circle = plt.Circle(
            (col, row),
            radius=0.4,
            facecolor=color,
            edgecolor="#2D3436",
            linewidth=2,
            alpha=0.8,
        )
        ax.add_patch(circle)

        # Etiqueta del antibiótico (abreviado)
        antibiotic_name = well["antibiotic"] or "CTRL"
        antibiotic_abbrev = antibiotic_name[:4].upper()
        ax.text(
            col,
            row - 0.05,
            antibiotic_abbrev,
            ha="center",
            va="center",
            fontsize=7,
            fontweight="bold",
            color="white"
            if family in ["Control Negativo", "Carbapenémicos"]
            else "black",
        )

        # Concentración
        if well["type"] != "control" and well.get("concentration") is not None:
            conc_text = f"{well['concentration']:.2g}"
            ax.text(
                col,
                row + 0.15,
                conc_text,
                ha="center",
                va="center",
                fontsize=6,
                color="white"
                if family in ["Control Negativo", "Carbapenémicos"]
                else "black",
            )

    # Título
    ax.set_title(
        f"Panel AST de 96 Pozos: {panel_name}\nP. aeruginosa - Susceptibilidad Antimicrobiana",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # Leyenda de familias
    legend_patches = []
    for family, color in ANTIBIOTIC_COLORS.items():
        # Contar cuántos wells de esta familia
        count = sum(1 for w in wells if w["family"] == family)
        if count > 0:
            patch = mpatches.Patch(
                color=color,
                label=f"{family} (n={count})",
                edgecolor="#2D3436",
                linewidth=1,
            )
            legend_patches.append(patch)

    ax.legend(
        handles=legend_patches,
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        fontsize=10,
        frameon=True,
        fancybox=True,
        shadow=True,
    )

    plt.tight_layout()

    # Guardar o mostrar
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
        print(f"✅ Diagrama guardado en: {save_path}")
    else:
        print("📊 Mostrando diagrama...")
        plt.show()

    plt.close()


def generate_concentration_heatmap(panel_name: str = "EUCAST_Pseudomonas"):
    """
    Genera mapa de calor de concentraciones del panel.

    Visualiza gradientes de dilución para cada antibiótico.
    """
    print(f"🌡️  Generando mapa de calor de concentraciones: {panel_name}")

    wells = load_panel_layout(panel_name)

    if not wells:
        return

    # Matriz de concentraciones (8x12)
    concentration_matrix = np.zeros((8, 12))
    labels = [["" for _ in range(12)] for _ in range(8)]

    for well in wells:
        row, col = well_to_row_col(well["position"])
        if well["type"] != "control":
            concentration_matrix[row, col] = well["concentration"]
            labels[row][col] = f"{well['antibiotic'][:3]}\n{well['concentration']:.2g}"
        else:
            concentration_matrix[row, col] = 0
            labels[row][col] = well["type"][:3].upper()

    # Crear heatmap
    fig, ax = plt.subplots(figsize=(14, 8))

    im = ax.imshow(concentration_matrix, cmap="YlOrRd", aspect="auto", vmin=0)

    # Etiquetas
    ax.set_xticks(range(12))
    ax.set_xticklabels([str(i + 1) for i in range(12)])
    ax.set_yticks(range(8))
    ax.set_yticklabels(["A", "B", "C", "D", "E", "F", "G", "H"])

    # Texto en cada celda
    for i in range(8):
        for j in range(12):
            text = ax.text(
                j, i, labels[i][j], ha="center", va="center", color="black", fontsize=7
            )

    ax.set_title(
        f"Mapa de Calor: Concentraciones Antibióticas (µg/mL)\n{panel_name}",
        fontsize=14,
        fontweight="bold",
    )

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Concentración (µg/mL)", rotation=270, labelpad=20)

    plt.tight_layout()
    plt.show()
    plt.close()


def main():
    """Función principal."""
    print("=" * 70)
    print("🧬 GENERADOR DE DIAGRAMA DE PANEL AST DE 96 POZOS")
    print("=" * 70)
    print()

    # Listar paneles disponibles
    session = get_session()
    panel_names = session.query(PanelLayout.panel_name).distinct().all()
    session.close()

    if not panel_names:
        print("❌ No hay paneles en la base de datos")
        return

    print("📋 Paneles disponibles:")
    for idx, (name,) in enumerate(panel_names, 1):
        print(f"  {idx}. {name}")
    print()

    # Generar diagrama para cada panel
    for (panel_name,) in panel_names:
        print(f"\n{'─' * 70}")
        generate_96well_diagram(panel_name)
        print()

    print("\n" + "=" * 70)
    print("✅ Generación completada exitosamente")
    print("=" * 70)


if __name__ == "__main__":
    main()
