from kfp.dsl import component, Output, Dataset

@component(
    base_image="python:3.10",
    packages_to_install=
    [
        "numpy==1.26.4",      # ← NumPy 1.x para evitar el choque
        "pandas==2.1.4",      # ← Compatible con NumPy 1.26
        "pyarrow==14.0.2",    # ← Compatible con NumPy 1.26 y Pandas 2.1
        "gcsfs==2024.2.0"     # ← Para leer gs:// con pandas
    ]
)
def load_data(
    csv_path: str,
    dataset: Output[Dataset],
):
    """
    Componente de Vertex AI Pipeline que carga un archivo CSV y lo guarda en formato Parquet.
    """
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    
    df = pd.read_csv(csv_path, parse_dates=["signup_date", "last_purchase_date"])
    print(f"[INFO] Leyendo CSV desde: {csv_path}")
    
    df.to_parquet(f"{dataset.path}.parquet", engine='pyarrow', index=False)   
    print(f"[INFO] Filas cargadas: {len(df)}")
    print(f"[INFO] Archivo Parquet guardado en: {dataset.path}.parquet")