"""
Herramientas de drift: PSI y chequeos simples.
"""

import numpy as np
import pandas as pd

def _bin_edges(series, n_bins=10):
    # Usa cuantiles para bins robustos
    quantiles = np.linspace(0, 1, n_bins+1)
    edges = series.quantile(quantiles).values
    # Evitar edges duplicados
    edges = np.unique(edges)
    if len(edges) < 3:
        # fallback a cortes uniformes si no hay suficiente variación
        edges = np.linspace(series.min(), series.max(), n_bins+1)
    return edges

def population_stability_index(ref: pd.Series, cur: pd.Series, n_bins: int = 10) -> float:
    """
    PSI: mide el cambio de distribución entre ref (baseline) y cur (actual).
    Interpretación común:
        < 0.1   → No significativo
        0.1-0.25→ Moderado
        > 0.25  → Severo
    """
    ref = pd.to_numeric(ref, errors="coerce").dropna()
    cur = pd.to_numeric(cur, errors="coerce").dropna()
    if ref.empty or cur.empty:
        return float("nan")

    edges = _bin_edges(ref, n_bins=n_bins)
    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)

    # Proporciones
    ref_prop = ref_counts / max(ref_counts.sum(), 1)
    cur_prop = cur_counts / max(cur_counts.sum(), 1)

    # Evitar logs de cero
    ref_prop = np.where(ref_prop == 0, 1e-6, ref_prop)
    cur_prop = np.where(cur_prop == 0, 1e-6, cur_prop)

    psi = np.sum((cur_prop - ref_prop) * np.log(cur_prop / ref_prop))
    return float(psi)

def drift_report(reference_df: pd.DataFrame, current_df: pd.DataFrame, features: list, n_bins: int = 10):
    """
    Retorna dict con PSI por feature.
    """
    report = {}
    for f in features:
        try:
            psi = population_stability_index(reference_df[f], current_df[f], n_bins=n_bins)
        except Exception:
            psi = float("nan")
        report[f] = psi
    return report
