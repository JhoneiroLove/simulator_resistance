"""
Generador de Diagrama Conceptual del Modelo Evolutivo
Figura 12. Diagrama conceptual del modelo evolutivo.

Este script genera visualizaciones del modelo matemático y computacional
del motor evolutivo, incluyendo:
- Estructura de datos de perfiles de resistencia y MIC
- Modelo logístico de crecimiento bacteriano
- Mecanismos de mutación y presión selectiva
- Cálculo de fitness y competencia
- Flujo lógico del algoritmo evolutivo

Autor: Sistema SRB
Fecha: Diciembre 2025
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np
import seaborn as sns

# Configuración de estilo
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["font.size"] = 9
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["figure.figsize"] = (18, 12)


def create_main_diagram():
    """Crea el diagrama principal del modelo evolutivo."""

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle(
        "Figura 12. Diagrama Conceptual del Modelo Evolutivo\n"
        + "Estructura Matemática y Computacional del Motor de Resistencia Bacteriana",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    # Crear grid de subplots
    gs = fig.add_gridspec(
        3, 3, hspace=0.4, wspace=0.3, left=0.05, right=0.95, top=0.93, bottom=0.05
    )

    # 1. Estructura de Datos (arriba izquierda)
    ax1 = fig.add_subplot(gs[0, 0])
    plot_data_structure(ax1)

    # 2. Modelo Logístico (arriba centro)
    ax2 = fig.add_subplot(gs[0, 1])
    plot_logistic_model(ax2)

    # 3. Mecanismo de Mutación (arriba derecha)
    ax3 = fig.add_subplot(gs[0, 2])
    plot_mutation_mechanism(ax3)

    # 4. Cálculo de Fitness (centro izquierda)
    ax4 = fig.add_subplot(gs[1, 0])
    plot_fitness_calculation(ax4)

    # 5. Flujo del Algoritmo (centro, ocupa 2 columnas)
    ax5 = fig.add_subplot(gs[1, 1:])
    plot_algorithm_flow(ax5)

    # 6. Presión Selectiva (abajo izquierda)
    ax6 = fig.add_subplot(gs[2, 0])
    plot_selective_pressure(ax6)

    # 7. Curvas de Crecimiento (abajo centro)
    ax7 = fig.add_subplot(gs[2, 1])
    plot_growth_curves(ax7)

    # 8. Mapa de MIC (abajo derecha)
    ax8 = fig.add_subplot(gs[2, 2])
    plot_mic_heatmap(ax8)

    return fig


def plot_data_structure(ax):
    """Diagrama de estructura de datos BacteriaProfile."""

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title(
        "A) Estructura de Datos: BacteriaProfile",
        fontweight="bold",
        fontsize=11,
        pad=10,
    )

    # Caja principal
    main_box = FancyBboxPatch(
        (0.5, 1),
        9,
        8.5,
        boxstyle="round,pad=0.1",
        edgecolor="#2c3e50",
        facecolor="#ecf0f1",
        linewidth=2,
    )
    ax.add_patch(main_box)

    # Título
    ax.text(
        5,
        9,
        "BacteriaProfile",
        ha="center",
        va="top",
        fontsize=12,
        fontweight="bold",
        color="#2c3e50",
    )

    # Campos
    fields = [
        ("organismo: str", "Pseudomonas aeruginosa"),
        ("escenario: str", '"hospitalizado" | "comunitario"'),
        ("origen_muestra: str", '"hemocultivo" | "esputo" | "orina"'),
        ("genotipo: Dict[str, str]", "{gen → estado_mutacional}"),
        ("mics_calculated: Dict[str, float]", "{antibiótico → MIC (µg/mL)}"),
        ("antibioticos_previos: List[str]", "Historial de exposición"),
        ("mutaciones_aplicadas: List[Dict]", "Metadata de mutaciones"),
    ]

    y_pos = 8
    for field, example in fields:
        # Nombre del campo
        ax.text(
            1,
            y_pos,
            f"• {field}",
            ha="left",
            va="top",
            fontsize=9,
            fontweight="bold",
            family="monospace",
            color="#16a085",
        )

        # Ejemplo
        ax.text(
            1.3,
            y_pos - 0.4,
            f"  ej: {example}",
            ha="left",
            va="top",
            fontsize=8,
            style="italic",
            color="#7f8c8d",
        )

        y_pos -= 1.1

    # Anotación
    ax.text(
        5,
        0.5,
        "Mapea a tabla SQL bacteria_profiles",
        ha="center",
        va="bottom",
        fontsize=8,
        style="italic",
        color="#e74c3c",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="#ffe6e6",
            edgecolor="#e74c3c",
            linewidth=1,
        ),
    )


def plot_logistic_model(ax):
    """Modelo matemático de crecimiento logístico."""

    ax.set_title(
        "B) Modelo Logístico de Crecimiento", fontweight="bold", fontsize=11, pad=10
    )

    # Ecuación
    ax.text(
        0.5,
        0.95,
        r"$OD(t) = OD_0 + \frac{OD_{max} - OD_0}{1 + e^{-k(t - t_{mid})}}$",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=13,
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor="#fff3cd",
            edgecolor="#f39c12",
            linewidth=2,
        ),
    )

    # Curva logística
    t = np.linspace(0, 1080, 500)  # 18 horas
    od_max = 2.0
    k = 0.02
    t_mid = 480
    od_0 = 0.05

    od = od_0 + (od_max - od_0) / (1 + np.exp(-k * (t - t_mid)))

    ax.plot(t / 60, od, linewidth=3, color="#27ae60", label="Curva logística")

    # Fase lag
    ax.axvspan(0, t_mid / 60 - 2, alpha=0.2, color="blue", label="Fase lag")
    # Fase exponencial
    ax.axvspan(
        t_mid / 60 - 2, t_mid / 60 + 2, alpha=0.2, color="red", label="Fase exponencial"
    )
    # Fase estacionaria
    ax.axvspan(t_mid / 60 + 2, 18, alpha=0.2, color="gray", label="Fase estacionaria")

    # Punto de inflexión
    ax.plot(
        t_mid / 60, od_max / 2, "ro", markersize=10, label=f"$t_{{mid}}$ = {t_mid} min"
    )
    ax.axhline(od_max / 2, color="red", linestyle="--", alpha=0.5, linewidth=1)
    ax.axvline(t_mid / 60, color="red", linestyle="--", alpha=0.5, linewidth=1)

    # Anotaciones
    ax.annotate(
        "$OD_{max}$",
        xy=(16, od_max),
        xytext=(14, od_max + 0.3),
        fontsize=11,
        ha="center",
        arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
    )

    ax.annotate(
        "$OD_0$ (inóculo)",
        xy=(0, od_0),
        xytext=(2, 0.3),
        fontsize=10,
        ha="left",
        arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
    )

    ax.set_xlabel("Tiempo (horas)", fontweight="bold")
    ax.set_ylabel("Densidad Óptica (OD₆₀₀)", fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.3, linestyle="--")
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 2.5)

    # Parámetros
    params_text = (
        "Parámetros:\n"
        f"• $k$ = {k} min⁻¹ (tasa crecimiento)\n"
        f"• $t_{{mid}}$ = {t_mid} min (punto inflexión)\n"
        f"• $OD_{{max}}$ = {od_max} (capacidad de carga)"
    )
    ax.text(
        0.02,
        0.5,
        params_text,
        transform=ax.transAxes,
        fontsize=8,
        verticalalignment="center",
        bbox=dict(
            boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", linewidth=1
        ),
    )


def plot_mutation_mechanism(ax):
    """Mecanismo de mutación con presión antibiótica."""

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title(
        "C) Mecanismo de Mutación Adaptativa", fontweight="bold", fontsize=11, pad=10
    )

    # Ecuación de probabilidad de mutación
    ax.text(
        5,
        9.5,
        r"$P_{mut} = \mu_{base} \cdot (1 + \alpha \cdot \frac{[ATB]}{MIC}) \cdot \Delta t$",
        ha="center",
        va="top",
        fontsize=12,
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor="#ffe6e6",
            edgecolor="#e74c3c",
            linewidth=2,
        ),
    )

    # Variables
    variables = [
        (r"$\mu_{base}$", "= 10⁻⁷ (tasa mutación basal)"),
        (r"$\alpha$", "= 100 (multiplicador de estrés)"),
        (r"$[ATB]$", "= concentración antibiótico (µg/mL)"),
        (r"$MIC$", "= concentración inhibitoria mínima"),
        (r"$\Delta t$", "= paso de tiempo (horas)"),
    ]

    y_pos = 8
    for var, desc in variables:
        ax.text(
            1,
            y_pos,
            f"{var} {desc}",
            ha="left",
            va="center",
            fontsize=9,
            family="monospace",
        )
        y_pos -= 0.8

    # Diagrama de flujo
    y_start = 4.5

    # Paso 1
    box1 = FancyBboxPatch(
        (1, y_start),
        8,
        0.8,
        boxstyle="round,pad=0.05",
        edgecolor="#3498db",
        facecolor="#d6eaf8",
        linewidth=2,
    )
    ax.add_patch(box1)
    ax.text(
        5,
        y_start + 0.4,
        "1. Calcular factor de estrés: σ = [ATB] / MIC",
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
    )

    # Flecha
    ax.arrow(
        5,
        y_start,
        0,
        -0.5,
        head_width=0.3,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 2
    y_start -= 1.3
    box2 = FancyBboxPatch(
        (1, y_start),
        8,
        0.8,
        boxstyle="round,pad=0.05",
        edgecolor="#e67e22",
        facecolor="#fdebd0",
        linewidth=2,
    )
    ax.add_patch(box2)
    ax.text(
        5,
        y_start + 0.4,
        r"2. Calcular P_mut efectiva con σ",
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
    )

    # Flecha
    ax.arrow(
        5,
        y_start,
        0,
        -0.5,
        head_width=0.3,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 3
    y_start -= 1.3
    box3 = FancyBboxPatch(
        (1, y_start),
        8,
        0.8,
        boxstyle="round,pad=0.05",
        edgecolor="#27ae60",
        facecolor="#d5f4e6",
        linewidth=2,
    )
    ax.add_patch(box3)
    ax.text(
        5,
        y_start + 0.4,
        "3. Muestreo estocástico: rand() < P_mut → MUTACIÓN",
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
    )

    # Resultado
    ax.text(
        5,
        0.3,
        "Si mutación ocurre: agregar gen de resistencia al genotipo",
        ha="center",
        va="center",
        fontsize=9,
        style="italic",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="#abebc6",
            edgecolor="#27ae60",
            linewidth=1.5,
        ),
    )


def plot_fitness_calculation(ax):
    """Cálculo de fitness con modelo multiplicativo."""

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title(
        "D) Cálculo de Fitness (Costo Biológico)",
        fontweight="bold",
        fontsize=11,
        pad=10,
    )

    # Ecuación principal
    ax.text(
        5,
        9.5,
        r"$CI_{total} = \prod_{i} CI_i$     (Competitive Index)",
        ha="center",
        va="top",
        fontsize=11,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor="#fff9e6",
            edgecolor="#f39c12",
            linewidth=2,
        ),
    )

    # Tabla de costos
    genes = ["oprD_loss", "blaVIM", "mexR_frameshift", "gyrA_T83I"]
    ci_values = [0.85, 0.65, 0.82, 0.92]
    fitness_costs = [0.15, 0.35, 0.18, 0.08]

    # Encabezados
    ax.text(2, 8, "Gen Mutado", ha="center", fontweight="bold", fontsize=9)
    ax.text(5, 8, "CI Individual", ha="center", fontweight="bold", fontsize=9)
    ax.text(8, 8, "Costo (%)", ha="center", fontweight="bold", fontsize=9)

    # Línea separadora
    ax.plot([1, 9], [7.7, 7.7], "k-", linewidth=1.5)

    # Datos
    y_pos = 7.2
    for gene, ci, cost in zip(genes, ci_values, fitness_costs):
        ax.text(2, y_pos, gene, ha="center", fontsize=8, family="monospace")
        ax.text(5, y_pos, f"{ci:.2f}", ha="center", fontsize=8)
        ax.text(8, y_pos, f"{cost * 100:.0f}%", ha="center", fontsize=8)
        y_pos -= 0.6

    # Línea separadora
    ax.plot([1, 9], [y_pos + 0.3, y_pos + 0.3], "k-", linewidth=1.5)

    # Resultado acumulado
    ci_total = np.prod(ci_values)
    y_pos -= 0.5
    ax.text(
        2,
        y_pos,
        "ACUMULADO",
        ha="center",
        fontweight="bold",
        fontsize=9,
        color="#c0392b",
    )
    ax.text(
        5,
        y_pos,
        f"{ci_total:.3f}",
        ha="center",
        fontweight="bold",
        fontsize=9,
        color="#c0392b",
    )
    ax.text(
        8,
        y_pos,
        f"{(1 - ci_total) * 100:.1f}%",
        ha="center",
        fontweight="bold",
        fontsize=9,
        color="#c0392b",
    )

    # Métricas derivadas
    metrics_text = (
        "Métricas Derivadas:\n\n"
        f"• Tasa crecimiento relativa: {ci_total:.2f}\n"
        f"• Tiempo duplicación: {20 / ci_total:.1f} min\n"
        f"  (vs wild-type: 20 min)\n"
        f"• Desventaja competitiva: {(1 - ci_total) * 100:.0f}%"
    )

    ax.text(
        5,
        2.5,
        metrics_text,
        ha="center",
        va="top",
        fontsize=8,
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor="#fdebd0",
            edgecolor="#e67e22",
            linewidth=1.5,
        ),
    )


def plot_algorithm_flow(ax):
    """Flujo lógico del algoritmo evolutivo."""

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title(
        "E) Flujo del Algoritmo Evolutivo (Generación n → n+1)",
        fontweight="bold",
        fontsize=12,
        pad=10,
    )

    box_width = 2.5
    box_height = 0.8
    y_start = 9

    # Paso 1: Inicialización
    x1 = 1
    box1 = FancyBboxPatch(
        (x1, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#2c3e50",
        facecolor="#ecf0f1",
        linewidth=2,
    )
    ax.add_patch(box1)
    ax.text(
        x1 + box_width / 2,
        y_start + box_height / 2,
        "Inicializar\nPoblación",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Flecha
    ax.arrow(
        x1 + box_width,
        y_start + box_height / 2,
        0.4,
        0,
        head_width=0.2,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 2: Calcular MIC
    x2 = x1 + box_width + 0.7
    box2 = FancyBboxPatch(
        (x2, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#3498db",
        facecolor="#d6eaf8",
        linewidth=2,
    )
    ax.add_patch(box2)
    ax.text(
        x2 + box_width / 2,
        y_start + box_height / 2,
        "Calcular MIC\n(genotipo→fenotipo)",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Flecha
    ax.arrow(
        x2 + box_width,
        y_start + box_height / 2,
        0.4,
        0,
        head_width=0.2,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 3: Aplicar tratamiento
    x3 = x2 + box_width + 0.7
    box3 = FancyBboxPatch(
        (x3, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#e74c3c",
        facecolor="#fadbd8",
        linewidth=2,
    )
    ax.add_patch(box3)
    ax.text(
        x3 + box_width / 2,
        y_start + box_height / 2,
        "Aplicar\nTratamiento ATB",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Flecha hacia abajo
    ax.arrow(
        x3 + box_width / 2,
        y_start,
        0,
        -0.5,
        head_width=0.2,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 4: Presión selectiva
    y_start -= 1.3
    x4 = x3
    box4 = FancyBboxPatch(
        (x4, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#e67e22",
        facecolor="#fdebd0",
        linewidth=2,
    )
    ax.add_patch(box4)
    ax.text(
        x4 + box_width / 2,
        y_start + box_height / 2,
        "Presión Selectiva\n([ATB] vs MIC)",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Flecha hacia izquierda
    ax.arrow(
        x4,
        y_start + box_height / 2,
        -0.4,
        0,
        head_width=0.2,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 5: Supervivencia
    x5 = x2
    box5 = FancyBboxPatch(
        (x5, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#27ae60",
        facecolor="#d5f4e6",
        linewidth=2,
    )
    ax.add_patch(box5)
    ax.text(
        x5 + box_width / 2,
        y_start + box_height / 2,
        "Supervivencia\n(MIC > [ATB])",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Flecha hacia izquierda
    ax.arrow(
        x5,
        y_start + box_height / 2,
        -0.4,
        0,
        head_width=0.2,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 6: Mutación
    x6 = x1
    box6 = FancyBboxPatch(
        (x6, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#9b59b6",
        facecolor="#ebdef0",
        linewidth=2,
    )
    ax.add_patch(box6)
    ax.text(
        x6 + box_width / 2,
        y_start + box_height / 2,
        "Intentar\nMutación",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Flecha hacia abajo
    ax.arrow(
        x6 + box_width / 2,
        y_start,
        0,
        -0.5,
        head_width=0.2,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 7: Fitness
    y_start -= 1.3
    x7 = x1
    box7 = FancyBboxPatch(
        (x7, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#f39c12",
        facecolor="#fff9e6",
        linewidth=2,
    )
    ax.add_patch(box7)
    ax.text(
        x7 + box_width / 2,
        y_start + box_height / 2,
        "Calcular Fitness\n(costo mutación)",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Flecha hacia derecha
    ax.arrow(
        x7 + box_width,
        y_start + box_height / 2,
        0.4,
        0,
        head_width=0.2,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 8: Crecimiento
    x8 = x2
    box8 = FancyBboxPatch(
        (x8, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#16a085",
        facecolor="#d0ece7",
        linewidth=2,
    )
    ax.add_patch(box8)
    ax.text(
        x8 + box_width / 2,
        y_start + box_height / 2,
        "Crecimiento\nLogístico",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Flecha hacia derecha
    ax.arrow(
        x8 + box_width,
        y_start + box_height / 2,
        0.4,
        0,
        head_width=0.2,
        head_length=0.15,
        fc="black",
        ec="black",
        linewidth=1.5,
    )

    # Paso 9: Nueva generación
    x9 = x3
    box9 = FancyBboxPatch(
        (x9, y_start),
        box_width,
        box_height,
        boxstyle="round,pad=0.05",
        edgecolor="#2ecc71",
        facecolor="#abebc6",
        linewidth=2,
    )
    ax.add_patch(box9)
    ax.text(
        x9 + box_width / 2,
        y_start + box_height / 2,
        "Generación n+1\n(nuevo ciclo)",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
    )

    # Anotaciones laterales
    annotations = [
        (10, 8.5, "INPUT:\nGenotipo\nTratamiento", "#3498db"),
        (10, 6.2, "PROCESO:\nSelección\nMutación", "#e67e22"),
        (10, 4, "OUTPUT:\nNueva población\ncon resistencia", "#27ae60"),
    ]

    for x, y, text, color in annotations:
        ax.text(
            x,
            y,
            text,
            ha="left",
            va="center",
            fontsize=8,
            bbox=dict(
                boxstyle="round,pad=0.4",
                facecolor="white",
                edgecolor=color,
                linewidth=2,
            ),
        )


def plot_selective_pressure(ax):
    """Gráfico de presión selectiva vs concentración."""

    ax.set_title(
        "F) Presión Selectiva de Antibiótico", fontweight="bold", fontsize=11, pad=10
    )

    # Concentraciones
    conc = np.linspace(0, 32, 500)
    mic = 8.0

    # Ecuación de Hill (inhibición)
    hill = 4.0
    inhibition = (conc / mic) ** hill / (1 + (conc / mic) ** hill)

    # Supervivencia
    survival = 1 - inhibition

    # Probabilidad de mutación (proporcional a estrés)
    base_mut = 1e-7
    alpha = 100
    mutation_prob = base_mut * (1 + alpha * (conc / mic))
    mutation_prob = np.clip(mutation_prob, 0, 0.1)

    # Normalizar para visualización
    mutation_prob_norm = mutation_prob / mutation_prob.max()

    # Plot
    ax.plot(
        conc,
        survival * 100,
        linewidth=2.5,
        color="#27ae60",
        label="Supervivencia (%)",
        linestyle="-",
    )
    ax.plot(
        conc,
        inhibition * 100,
        linewidth=2.5,
        color="#e74c3c",
        label="Inhibición (%)",
        linestyle="--",
    )
    ax.plot(
        conc,
        mutation_prob_norm * 100,
        linewidth=2.5,
        color="#9b59b6",
        label="P(mutación) normalizada",
        linestyle=":",
    )

    # MIC
    ax.axvline(
        mic,
        color="black",
        linestyle="--",
        linewidth=2,
        alpha=0.7,
        label=f"MIC = {mic} µg/mL",
    )

    # Zonas
    ax.axvspan(0, mic, alpha=0.15, color="green", label="Zona sensible")
    ax.axvspan(mic, 32, alpha=0.15, color="red", label="Zona resistente")

    ax.set_xlabel("Concentración Antibiótico (µg/mL)", fontweight="bold")
    ax.set_ylabel("Porcentaje (%)", fontweight="bold")
    ax.legend(loc="center left", fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.3, linestyle="--")
    ax.set_xlim(0, 32)
    ax.set_ylim(0, 105)


def plot_growth_curves(ax):
    """Curvas de crecimiento con diferentes fitness."""

    ax.set_title(
        "G) Curvas de Crecimiento según Fitness", fontweight="bold", fontsize=11, pad=10
    )

    t = np.linspace(0, 1080, 500)

    # Wild-type (sin costo)
    od_wt = 0.05 + (2.0 - 0.05) / (1 + np.exp(-0.02 * (t - 480)))

    # 1 mutación (CI = 0.85)
    od_1mut = 0.05 + (2.0 * 0.85 - 0.05) / (1 + np.exp(-0.02 * 0.85 * (t - 480 * 1.1)))

    # 2 mutaciones (CI = 0.70)
    od_2mut = 0.05 + (2.0 * 0.70 - 0.05) / (1 + np.exp(-0.02 * 0.70 * (t - 480 * 1.2)))

    # 3 mutaciones (CI = 0.50)
    od_3mut = 0.05 + (2.0 * 0.50 - 0.05) / (1 + np.exp(-0.02 * 0.50 * (t - 480 * 1.4)))

    ax.plot(
        t / 60,
        od_wt,
        linewidth=2.5,
        color="#27ae60",
        label="Wild-type (CI=1.0)",
        linestyle="-",
    )
    ax.plot(
        t / 60,
        od_1mut,
        linewidth=2.5,
        color="#3498db",
        label="1 mutación (CI=0.85)",
        linestyle="--",
    )
    ax.plot(
        t / 60,
        od_2mut,
        linewidth=2.5,
        color="#f39c12",
        label="2 mutaciones (CI=0.70)",
        linestyle="-.",
    )
    ax.plot(
        t / 60,
        od_3mut,
        linewidth=2.5,
        color="#e74c3c",
        label="3 mutaciones (CI=0.50)",
        linestyle=":",
    )

    ax.set_xlabel("Tiempo (horas)", fontweight="bold")
    ax.set_ylabel("Densidad Óptica (OD₆₀₀)", fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.3, linestyle="--")
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 2.2)

    # Anotación
    ax.text(
        0.98,
        0.5,
        "Costo de fitness\nretrasa y reduce\nel crecimiento",
        transform=ax.transAxes,
        ha="right",
        va="center",
        fontsize=9,
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor="#ffe6e6",
            edgecolor="#e74c3c",
            linewidth=1.5,
        ),
    )


def plot_mic_heatmap(ax):
    """Mapa de calor de MICs calculados."""

    ax.set_title(
        "H) Mapa de MICs: Genotipo → Fenotipo", fontweight="bold", fontsize=11, pad=10
    )

    # Datos simulados
    antibiotics = [
        "Imipenem",
        "Meropenem",
        "Ceftazidima",
        "Ciprofloxacina",
        "Gentamicina",
        "Amikacina",
    ]
    genotypes = [
        "Wild-type",
        "oprD⁻",
        "oprD⁻ + blaVIM",
        "oprD⁻ + blaVIM\n+ mexR⁻",
        "Multi-resistente",
    ]

    # Matriz de MICs (log2)
    mics = np.array(
        [
            [1, 1, 2, 0.5, 2, 4],  # Wild-type
            [4, 4, 2, 0.5, 2, 4],  # oprD-
            [32, 32, 16, 0.5, 2, 4],  # oprD- + blaVIM
            [64, 64, 64, 16, 2, 4],  # + mexR-
            [128, 128, 128, 64, 32, 16],  # Multi-resistente
        ]
    )

    # Log2 transform para mejor visualización
    mics_log = np.log2(mics + 0.1)

    # Heatmap
    im = ax.imshow(mics_log, cmap="YlOrRd", aspect="auto", interpolation="nearest")

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("MIC (log₂ µg/mL)", fontweight="bold", fontsize=9)

    # Etiquetas
    ax.set_xticks(np.arange(len(antibiotics)))
    ax.set_yticks(np.arange(len(genotypes)))
    ax.set_xticklabels(antibiotics, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(genotypes, fontsize=8)

    # Valores en celdas
    for i in range(len(genotypes)):
        for j in range(len(antibiotics)):
            text = ax.text(
                j,
                i,
                f"{mics[i, j]:.0f}",
                ha="center",
                va="center",
                color="black",
                fontsize=8,
                fontweight="bold",
            )

    # Anotación
    ax.text(
        0.5,
        -0.25,
        "Modelo multiplicativo: MIC_final = MIC_base × ∏(multiplicadores)",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=8,
        style="italic",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="#fff3cd",
            edgecolor="#f39c12",
            linewidth=1,
        ),
    )


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" GENERADOR DE DIAGRAMAS DEL MODELO EVOLUTIVO")
    print(" Figura 12. Diagrama conceptual del modelo evolutivo")
    print("=" * 80 + "\n")

    print("Generando 8 figuras independientes...\n")

    # Lista para almacenar todas las figuras
    figures = []

    # Figura 12A: Estructura de Datos
    print("[1/8] Generando Figura 12A - Estructura de Datos...")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    plot_data_structure(ax1)
    fig1.suptitle(
        "Figura 12A. Estructura de Datos: BacteriaProfile",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    figures.append(("12A_EstructuraDatos", fig1))

    # Figura 12B: Modelo Logístico
    print("[2/8] Generando Figura 12B - Modelo Logístico...")
    fig2, ax2 = plt.subplots(figsize=(10, 7))
    plot_logistic_model(ax2)
    fig2.suptitle(
        "Figura 12B. Modelo Logístico de Crecimiento Bacteriano",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    figures.append(("12B_ModeloLogistico", fig2))

    # Figura 12C: Mecanismo de Mutación
    print("[3/8] Generando Figura 12C - Mecanismo de Mutación...")
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    plot_mutation_mechanism(ax3)
    fig3.suptitle(
        "Figura 12C. Mecanismo de Mutación Adaptativa", fontsize=14, fontweight="bold"
    )
    plt.tight_layout()
    figures.append(("12C_MecanismoMutacion", fig3))

    # Figura 12D: Cálculo de Fitness
    print("[4/8] Generando Figura 12D - Cálculo de Fitness...")
    fig4, ax4 = plt.subplots(figsize=(10, 8))
    plot_fitness_calculation(ax4)
    fig4.suptitle(
        "Figura 12D. Cálculo de Fitness (Costo Biológico)",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    figures.append(("12D_CalculoFitness", fig4))

    # Figura 12E: Flujo del Algoritmo
    print("[5/8] Generando Figura 12E - Flujo del Algoritmo...")
    fig5, ax5 = plt.subplots(figsize=(14, 8))
    plot_algorithm_flow(ax5)
    fig5.suptitle(
        "Figura 12E. Flujo del Algoritmo Evolutivo (Generación n → n+1)",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    figures.append(("12E_FlujoAlgoritmo", fig5))

    # Figura 12F: Presión Selectiva
    print("[6/8] Generando Figura 12F - Presión Selectiva...")
    fig6, ax6 = plt.subplots(figsize=(10, 7))
    plot_selective_pressure(ax6)
    fig6.suptitle(
        "Figura 12F. Presión Selectiva de Antibiótico", fontsize=14, fontweight="bold"
    )
    plt.tight_layout()
    figures.append(("12F_PresionSelectiva", fig6))

    # Figura 12G: Curvas de Crecimiento
    print("[7/8] Generando Figura 12G - Curvas de Crecimiento...")
    fig7, ax7 = plt.subplots(figsize=(10, 7))
    plot_growth_curves(ax7)
    fig7.suptitle(
        "Figura 12G. Curvas de Crecimiento según Fitness",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    figures.append(("12G_CurvasCrecimiento", fig7))

    # Figura 12H: Mapa de MIC
    print("[8/8] Generando Figura 12H - Mapa de MICs...")
    fig8, ax8 = plt.subplots(figsize=(10, 8))
    plot_mic_heatmap(ax8)
    fig8.suptitle(
        "Figura 12H. Mapa de MICs: Genotipo → Fenotipo", fontsize=14, fontweight="bold"
    )
    plt.tight_layout()
    figures.append(("12H_MapaMICs", fig8))

    print("\n✓ Todas las figuras generadas exitosamente!")
    print("\nFiguras creadas:")
    print("  12A) Estructura de Datos: BacteriaProfile")
    print("  12B) Modelo Logístico de Crecimiento")
    print("  12C) Mecanismo de Mutación Adaptativa")
    print("  12D) Cálculo de Fitness (Costo Biológico)")
    print("  12E) Flujo del Algoritmo Evolutivo")
    print("  12F) Presión Selectiva de Antibiótico")
    print("  12G) Curvas de Crecimiento según Fitness")
    print("  12H) Mapa de MICs: Genotipo → Fenotipo")

    print("\nCERRAR CADA VENTANA para avanzar a la siguiente...")
    print("(Las figuras se mostrarán secuencialmente)\n")

    # Mostrar figuras secuencialmente
    for name, fig in figures:
        plt.figure(fig.number)
        plt.show()

    print("\n" + "=" * 80)
    print(" INFORMACIÓN TÉCNICA DEL MODELO")
    print("=" * 80)
    print("\n1. ECUACIONES FUNDAMENTALES:")
    print(
        "   • Crecimiento logístico: OD(t) = OD₀ + (OD_max - OD₀)/(1 + e^(-k(t-t_mid)))"
    )
    print("   • Mutación adaptativa: P_mut = μ_base × (1 + α × [ATB]/MIC) × Δt")
    print("   • Fitness acumulado: CI_total = ∏ CI_i")
    print("   • Inhibición (Hill): I = ([ATB]/MIC)^n / (1 + ([ATB]/MIC)^n)")
    print("\n2. PARÁMETROS CLAVE:")
    print("   • μ_base = 10⁻⁷ (tasa mutación basal)")
    print("   • α = 100 (multiplicador estrés antibiótico)")
    print("   • k = 0.02 min⁻¹ (tasa crecimiento)")
    print("   • n = 4 (coeficiente de Hill)")
    print("\n3. ESTRUCTURA DE DATOS:")
    print("   • BacteriaProfile: organismo, genotipo, MICs, escenario, historial")
    print("   • Genotipo: Dict[gen → estado_mutacional]")
    print("   • MICs: Dict[antibiótico → concentración (µg/mL)]")
    print("\n4. FLUJO COMPUTACIONAL:")
    print("   • Inicialización → Cálculo MIC → Tratamiento → Presión selectiva")
    print("   • → Supervivencia → Mutación → Fitness → Crecimiento → Nueva generación")
    print("\n" + "=" * 80 + "\n")
