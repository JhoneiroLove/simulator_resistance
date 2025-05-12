import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics import confusion_matrix


def exponential_growth(base_fit: float, mut_rate: float, time: float) -> float:
    """
    Modelo de crecimiento exponencial:
      factor = exp(mut_rate * time)
    """
    return float(np.exp(mut_rate * time))


def logistic_growth(
    base_fit: float, mut_rate: float, time: float, K: float = 1.0
) -> float:
    """
    Modelo de crecimiento logístico:
      N(t) = K / (1 + ((K - N0)/N0) * exp(-r * t))
    Devolveremos el factor N(t) / N0.
    """
    if base_fit <= 0:
        return 1.0
    # r ≈ mut_rate aquí, K valor de carga (puedes parametrizarlo)
    Nt = K / (1 + ((K - base_fit) / base_fit) * np.exp(-mut_rate * time))
    return float(Nt / base_fit)


def predict_MIC(
    ga, selected_genes: List[int], antibiotico, conc_list: List[float]
) -> float:
    """
    I1: Predice la CIM como la menor concentración en la que la resistencia
    promedio final sea ≤ 50% (o tu umbral).
    """
    for c in sorted(conc_list):
        best, avg = ga.run(
            selected_genes, concentration=c, time_horizon=ga.generations
        )[0:2]
        if avg[-1] <= 0.5:
            return c
    # si nunca cae, devolvemos la máxima
    return max(conc_list)


def predict_MPC(
    ga, selected_genes: List[int], antibiotico, conc_list: List[float]
) -> float:
    """
    I2: Predice la CPM como la menor concentración en la que la resistencia máxima
    final sea ≤ 50% (o tu umbral).
    """
    for c in sorted(conc_list):
        best, avg = ga.run(
            selected_genes, concentration=c, time_horizon=ga.generations
        )[0:2]
        if best[-1] <= 0.5:
            return c
    return max(conc_list)


def identify_MDR_XDR(
    res_dict: Dict[str, float], breakpoints: Dict[str, float]
) -> Tuple[bool, bool]:
    """
    I3: A partir de un diccionario antibiótico→resistencia_predicha
    y de los breakpoints CLSI, devuelve (es_MDR, es_XDR).
    """
    # MDR: resistencia a ≥ 1 antibiótico en ≥ 3 categorías
    # XDR: resistencia a ≥ 1 antibiótico en ≥ 6 categorías
    # Aquí simplificamos: contamos cuantos 'R' hay según breakpoint
    count_R = sum(1 for ab, val in res_dict.items() if val >= breakpoints.get(ab, 0.5))
    es_mdr = count_R >= 3
    es_xdr = count_R >= 6
    return es_mdr, es_xdr


def epcim(predicted: float, true: float) -> float:
    """
    1. Error porcentual en la CIM = |pred - true| / true * 100
    """
    if true == 0:
        return 0.0
    return abs(predicted - true) / true * 100.0


def pccpm(preds: List[float], trues: List[float]) -> float:
    """
    2. % Coincidencia en CPM = (número de predicciones exactas) / total * 100
    """
    matched = sum(1 for p, t in zip(preds, trues) if p == t)
    return matched / len(trues) * 100.0 if trues else 0.0


def ecmdr(pred_labels: List[str], true_labels: List[str]) -> float:
    """
    3. Exactitud de clasificación MDR/XDR (accuracy)
    """
    if not true_labels:
        return 0.0
    cm = confusion_matrix(true_labels, pred_labels, labels=["S", "MDR", "XDR"])
    correct = cm.trace()
    total = cm.sum()
    return correct / total * 100.0
