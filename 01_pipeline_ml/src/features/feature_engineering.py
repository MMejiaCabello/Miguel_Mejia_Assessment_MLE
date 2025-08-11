from kfp.dsl import component, Input, Output, Dataset

@component(
    base_image="python:3.10",
    packages_to_install=[
        "numpy==1.26.4",
        "pandas==2.1.4",
        "pyarrow==14.0.2",
    ]
)
def feature_engineering(
    input_parquet: Input[Dataset],
    engineered_dataset: Output[Dataset],
):
    """
    Lee un Parquet producido por el paso de ingesta, calcula 3 features y guarda otro Parquet.
    Features:
      - days_since_last_purchase
      - customer_tenure_days
      - value_x_purchases
    """
    import pandas as pd
    from datetime import datetime, timezone
    from pathlib import Path

    in_path = f"{input_parquet.path}.parquet"
    print(f"[INFO] Leyendo parquet de entrada: {in_path}")
    df = pd.read_parquet(in_path)

    # Asegurar que las fechas estén en formato datetime (por si el parquet no preservó tipo)
    if df["signup_date"].dtype.kind != "M":
        df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    if df["last_purchase_date"].dtype.kind != "M":
        df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"], errors="coerce")

    # 'Hoy' en UTC (Vertex usa zona neutral; si prefieres Lima: usa tz='America/Lima' con dateutil/pytz)
    today = pd.Timestamp(datetime.now(timezone.utc).date())

    # 1) Días desde última compra
    df["days_since_last_purchase"] = (today - df["last_purchase_date"]).dt.days

    # 2) Antigüedad del cliente (en días)
    df["customer_tenure_days"] = (today - df["signup_date"]).dt.days

    # 3) Interacción: valor promedio * total de compras
    # Manejo básico de nulos
    df["avg_purchase_value"] = pd.to_numeric(df["avg_purchase_value"], errors="coerce")
    df["total_purchases"] = pd.to_numeric(df["total_purchases"], errors="coerce")
    df["value_x_purchases"] = (df["avg_purchase_value"].fillna(0) * df["total_purchases"].fillna(0)).astype(float)

    # Opcional: Si hay fechas faltantes, days_since_last_purchase/tenure quedan NaN. Puedes imputar si deseas:
    # df["days_since_last_purchase"] = df["days_since_last_purchase"].fillna(99999)
    # df["customer_tenure_days"] = df["customer_tenure_days"].fillna(0)

    df.to_parquet(f"{engineered_dataset.path}.parquet", index=False, engine="pyarrow")

    print(f"[INFO] Filas procesadas: {len(df)}")
    print(f"[INFO] Parquet con features guardado en: {engineered_dataset.path}")
