#!/bin/bash
# Levanta servidor MLflow local (puede adaptarse a GCS o backend remoto)
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 --port 5000
