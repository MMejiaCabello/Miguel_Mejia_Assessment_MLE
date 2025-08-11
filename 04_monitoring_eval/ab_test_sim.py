"""
Simulador A/B: compara métricas entre dos variantes (v1 vs v2).
Se espera un DataFrame con columnas: y_true, y_proba_v1, y_pred_v1, y_proba_v2, y_pred_v2
"""
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

def evaluate_ab(df):
    def summarize(prefix):
        y_true = df["y_true"].astype(int)
        y_pred = df[f"y_pred_{prefix}"].astype(int)
        y_proba = df[f"y_proba_{prefix}"].astype(float)
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "f1": float(f1_score(y_true, y_pred)),
            "roc_auc": float(roc_auc_score(y_true, y_proba))
        }
    return {"v1": summarize("v1"), "v2": summarize("v2")}

def pick_winner(metrics_dict, primary="roc_auc", secondary="f1"):
    v1 = metrics_dict["v1"]
    v2 = metrics_dict["v2"]
    # Gana v2 si es >= en primario y no peor en secundario
    if (v2[primary] >= v1[primary]) and (v2[secondary] >= v1[secondary]):
        return "v2"
    return "v1"
