from google.cloud import aiplatform

# Inicializa el cliente con tu proyecto y región
def main():
    aiplatform.init(
        project="dev-farma-analytics-workspace",      # ← Reemplaza esto
        location="us-central1",             # ← Reemplaza si usas otra región
        staging_bucket="gs://assessment-mle"   # ← Reemplaza con tu bucket
    )

    # Ejecuta el pipeline
    job = aiplatform.PipelineJob(
        display_name="pipeline-churn-clientes",
        template_path="compiled/churn_pipeline.yaml",
        pipeline_root="gs://assessment-mle/pipeline-root/",  # Ruta donde se almacenan artefactos
        enable_caching=True,
        parameter_values={
            "csv_path": "gs://assessment-mle/datasets/clientes.csv",
            "auc_threshold": 0.40,
            "project_id": "dev-farma-analytics-workspace",
            "region": "us-central1",
            "model_display_name": "churn-xgb",
        }
    )

    job.submit()
    
if __name__ == "__main__":
    main()