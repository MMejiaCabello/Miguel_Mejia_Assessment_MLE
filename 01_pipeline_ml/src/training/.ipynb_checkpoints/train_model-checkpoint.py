from kfp.dsl import component, Input, Output, Dataset, Model, Metrics, OutputPath

@component(
    base_image="python:3.10",
    packages_to_install=[
        "numpy==1.26.4",
        "pandas==2.1.4",
        "pyarrow==14.0.2",
        "xgboost==1.7.6",
        "scikit-learn==1.3.2"
    ]
)
def train_model(
    preprocessed_dataset: Input[Dataset],
    model_artifact: Output[Model],
    metrics_artifact: Output[Metrics],
    roc_auc_out: OutputPath(float),  # ← salida primitiva para condicionar el pipeline
):
    """
    Entrena XGBoost para churn y emite métricas + modelo.
    """
    import numpy as np
    import pandas as pd
    import xgboost as xgb
    from pathlib import Path
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

    df = pd.read_parquet(f"{preprocessed_dataset.path}.parquet")

    # Definir features y target
    drop_non_features = [
        "customer_id","signup_date","last_purchase_date","churned"
    ]
    feature_cols = [c for c in df.columns if c not in drop_non_features]
    X = df[feature_cols]
    y = df["churned"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        tree_method="hist"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    # auc = float(roc_auc_score(y_test, y_proba))    
    if len(np.unique(y_test)) < 2:
        auc = 0.5  # baseline cuando no hay clases positivas/negativas en el split
    else:
        auc = float(roc_auc_score(y_test, y_proba))

    print(f"[METRICS] accuracy={acc:.4f} f1={f1:.4f} roc_auc={auc:.4f}")

    # Log en Metrics
    metrics_artifact.log_metric("accuracy", acc)
    metrics_artifact.log_metric("f1_score", f1)
    metrics_artifact.log_metric("roc_auc", auc)

    # Salida primitiva para gating
    with open(roc_auc_out, "w") as f:
        f.write(str(auc))

    # Guardar modelo
    out_dir = Path(model_artifact.path)
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_model(out_dir / "model.json")
    
    print(f"[INFO] Modelo guardado en {out_dir / 'model.json'}")
