# 03 – Versionado y Reentrenamiento

Este módulo define la política de promoción y reentrenamiento del modelo de Churn.

## Modos de comparación
- **GCS**: compara `metrics.json` del último run vs. `best/metrics.json`.
- **MLflow**: compara el mejor run del experimento vs. el run más reciente.

## Uso (GCS)
```bash
python compare_metrics.py gcs \
  --new gs://<bucket>/models/churn/<ts>/metrics.json \
  --best gs://<bucket>/models/churn/best/metrics.json \
  --metric f1_score --threshold 0.005 --emit_exitcode
```