from kfp.dsl import component, Input, Output, Dataset

@component(
    base_image="python:3.10",
    packages_to_install=[
        "numpy==1.26.4",
        "pandas==2.1.4",
        "pyarrow==14.0.2",
    ]
)
def preprocess_dataset(
    engineered_dataset: Input[Dataset],
    preprocessed_dataset: Output[Dataset],
):
    """
    Limpia, valida y normaliza tipos. Deja el dataset listo para training.
    Valida:
      - Columnas requeridas
      - Rangos básicos (no negativos)
    Transforma:
      - gender -> {Male:1, Female:0, otros:NaN}
      - casteo de tipos numéricos
      - imputa NaN numéricos con mediana (simple)
    """
    import pandas as pd
    import numpy as np
    from pathlib import Path

    in_path = f"{engineered_dataset.path}.parquet"
    df = pd.read_parquet(in_path)

    required_cols = [
        "customer_id","age","gender","signup_date","last_purchase_date",
        "total_purchases","avg_purchase_value","is_active","churned",
        "days_since_last_purchase","customer_tenure_days","value_x_purchases"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    # Tipos
    num_cols = ["age","total_purchases","avg_purchase_value",
                "is_active","days_since_last_purchase","customer_tenure_days",
                "value_x_purchases"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # gender a binario
    df["gender"] = df["gender"].map({"Male":1, "Female":0})
    # is_active a 0/1
    df["is_active"] = df["is_active"].fillna(0).astype(int)

    # Validaciones básicas (no negativos en columnas clave)
    for c in ["age","total_purchases","avg_purchase_value",
              "days_since_last_purchase","customer_tenure_days"]:
        if (df[c] < 0).any():
            raise ValueError(f"Valores negativos en {c}")

    # Imputación simple (mediana) para numéricos
    for c in num_cols:
        df[c] = df[c].fillna(df[c].median())

    # Imputa gender faltante con moda (0/1)
    df["gender"] = df["gender"].fillna(df["gender"].mode().iloc[0] if not df["gender"].dropna().empty else 0).astype(int)

    # Guardar
    # out_dir = Path(preprocessed_dataset.path)
    # out_dir.mkdir(parents=True, exist_ok=True)
    # out_path = out_dir / "clientes_preprocessed.parquet"
    # df.to_parquet(out_path, index=False, engine="pyarrow")
    
    df.to_parquet(f"{preprocessed_dataset.path}.parquet", index=False, engine="pyarrow")

    print(f"[INFO] Preprocesamiento OK. Filas: {len(df)}")
    print(f"[INFO] Guardado en: {preprocessed_dataset.path}")
