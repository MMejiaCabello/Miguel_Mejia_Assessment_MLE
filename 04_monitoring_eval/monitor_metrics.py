"""
Monitoreo de métricas y drift.
Uso:

# Crear baseline desde un dataset tabular etiquetado (train/valid split simple)
python monitor_metrics.py --make-baseline --data-path ../clientes.csv

# Correr chequeo sobre un batch "actual" (puedes simular drift con --simulate-drift)
python monitor_metrics.py --data-path ../clientes.csv --simulate-drift
"""
import argparse, json, sys, os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.linear_model import LogisticRegression

from drift_utils import drift_report

BASELINE_FILE = "baseline_metrics.json"

DEFAULT_THRESHOLDS = {
    "auc_min": 0.75,
    "auc_drop_pct_warn": 0.05,  # 5%
    "psi_warn": 0.1,
    "psi_severe": 0.25,
}

def compute_metrics(y_true, y_pred, y_proba):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred)),
        "recall": float(recall_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
    }

def make_baseline(df, target_col="churned"):
    # features básicos
    drop_cols = ["customer_id","signup_date","last_purchase_date", target_col]
    features = [c for c in df.columns if c not in drop_cols]
    X = pd.get_dummies(df[features], drop_first=True)
    y = df[target_col].astype(int)

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_tr, y_tr)
    proba = clf.predict_proba(X_te)[:,1]
    pred = (proba >= 0.5).astype(int)

    metrics = compute_metrics(y_te, pred, proba)

    baseline = {
        "features": X.columns.tolist(),
        "metrics": metrics,
        "n_valid": int(len(y_te)),
        "created_at": pd.Timestamp.utcnow().isoformat(),
        "notes": "Baseline computed with LogisticRegression split 80/20."
    }
    return baseline, X_te, y_te, proba, pred

def simulate_current_batch(df_ref, noise=0.2, target_col="churned"):
    """Crea un batch 'actual' perturbando algunas columnas numéricas para simular drift."""
    df = df_ref.copy()
    num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).columns.tolist()
    num_cols = [c for c in num_cols if c not in [target_col]]
    for c in num_cols:
        df[c] = df[c] * (1 + noise*np.random.randn(len(df)))
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-path", type=str, required=True, help="Ruta a clientes.csv")
    ap.add_argument("--make-baseline", action="store_true", help="Genera baseline y guarda baseline_metrics.json")
    ap.add_argument("--simulate-drift", action="store_true", help="Simula un batch actual con drift en numéricos")
    ap.add_argument("--thresholds-json", type=str, default=None, help="Archivo JSON con umbrales")
    args = ap.parse_args()

    thresholds = DEFAULT_THRESHOLDS.copy()
    if args.thresholds_json and os.path.exists(args.thresholds_json):
        thresholds.update(json.loads(Path(args.thresholds_json).read_text()))

    df = pd.read_csv(args.data_path, parse_dates=["signup_date","last_purchase_date"])

    if args.make_baseline:
        baseline, X_val, y_val, proba, pred = make_baseline(df)
        Path(BASELINE_FILE).write_text(json.dumps(baseline, indent=2))
        print("[OK] Baseline guardado en", BASELINE_FILE)
        print(json.dumps(baseline, indent=2))
        sys.exit(0)

    # Cargar baseline existente
    if not os.path.exists(BASELINE_FILE):
        print(f"[ERROR] No existe {BASELINE_FILE}. Ejecuta con --make-baseline primero.", file=sys.stderr)
        sys.exit(2)

    baseline = json.loads(Path(BASELINE_FILE).read_text())
    feat_ref = baseline["features"]

    # Construir dataset actual (simulado)
    df_cur = simulate_current_batch(df) if args.simulate_drift else df.copy()

    # Armar matrices con mismas dummies
    drop_cols = ["customer_id","signup_date","last_purchase_date","churned"]
    features = [c for c in df_cur.columns if c not in drop_cols]
    X_cur = pd.get_dummies(df_cur[features], drop_first=True)
    X_cur = X_cur.reindex(columns=feat_ref, fill_value=0)

    # Entrenar de nuevo en todo el dataset (simulación) y evaluar sobre el mismo split de baseline
    # En un sistema real, se evalúa sobre labeled feedback reciente o cohortes definidas
    from sklearn.linear_model import LogisticRegression
    X_all = pd.get_dummies(df[features], drop_first=True).reindex(columns=feat_ref, fill_value=0)
    y_all = df["churned"].astype(int)
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_all, y_all)

    # "Current" evaluation: usamos un sample aleatorio del actual
    cur_idx = np.random.choice(np.arange(len(X_cur)), size=min(2000, len(X_cur)), replace=False)
    X_eval = X_cur.iloc[cur_idx]
    y_eval = y_all.iloc[cur_idx] if len(y_all) == len(X_cur) else y_all.sample(len(X_eval), random_state=42)
    proba_cur = clf.predict_proba(X_eval)[:,1]
    pred_cur = (proba_cur >= 0.5).astype(int)

    metrics_cur = compute_metrics(y_eval, pred_cur, proba_cur)
    metrics_base = baseline["metrics"]

    # Drift (PSI) sobre features numéricos originales (aprox. usando columnas sin dummies)
    num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).columns.tolist()
    num_cols = [c for c in num_cols if c not in ["churned"]]
    psi = drift_report(df[num_cols], df_cur[num_cols], features=num_cols)

    # Reglas de alerta
    alerts = []
    if metrics_cur["roc_auc"] < thresholds["auc_min"]:
        alerts.append(f"ROC AUC actual {metrics_cur['roc_auc']:.3f} < mínimo {thresholds['auc_min']:.3f}")

    auc_drop = (metrics_base["roc_auc"] - metrics_cur["roc_auc"]) / max(metrics_base["roc_auc"], 1e-6)
    if auc_drop >= thresholds["auc_drop_pct_warn"]:
        alerts.append(f"Caída relativa de AUC {auc_drop*100:.1f}% ≥ {thresholds['auc_drop_pct_warn']*100:.0f}%")

    psi_severe = [f for f,v in psi.items() if v is not None and v > thresholds["psi_severe"]]
    psi_warn = [f for f,v in psi.items() if v is not None and thresholds["psi_warn"] <= v <= thresholds["psi_severe"]]
    if psi_severe:
        alerts.append(f"PSI severo en: {', '.join(psi_severe)}")
    if psi_warn:
        alerts.append(f"PSI moderado en: {', '.join(psi_warn)}")

    report = {
        "metrics_current": metrics_cur,
        "metrics_baseline": metrics_base,
        "auc_drop_pct": float(auc_drop),
        "psi": psi,
        "alerts": alerts,
        "generated_at": pd.Timestamp.utcnow().isoformat()
    }

    Path("monitor_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

    # Exit code no-cero si hay alertas (útil para Jobs/alerting)
    sys.exit(1 if alerts else 0)

if __name__ == "__main__":
    main()
