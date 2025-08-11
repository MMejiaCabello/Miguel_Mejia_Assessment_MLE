import kfp
# from kfp.dsl import Dataset, Input, Output, importer
from src.ingestion.load_data import load_data
from src.features.feature_engineering import feature_engineering
from src.preprocessing.preprocess import preprocess_dataset
from src.training.train_model import train_model
from src.deployment.register_model import register_model


@kfp.dsl.component(base_image="python:3.10")
def model_not_ok(msg: str):
    # Componente mínimo para dejar constancia cuando el modelo no pasa el umbral
    print(f"[MODEL NOT OK] {msg}")

@kfp.dsl.pipeline(
    name="churn-prediction-pipeline",
    description="Pipeline E2E: ingestión → FE → preproc → training + gate → registro"
)
def main_pipeline(
    csv_path: str = "gs://assessment-mle/datasets/clientes.csv",
    auc_threshold: float = 0.70,
    project_id: str = "dev-farma-analytics-workspace",
    region: str = "us-central1",
    model_display_name: str = "churn-xgb",
    serving_image_uri: str = "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-7:latest",
):
    
    # parquet_output = Dataset(name="clientes_parquet")
    
    load_data_task = load_data(
        csv_path=csv_path
    )
    load_data_task.set_display_name("Ingestion")
    
    feature_engineering_task = feature_engineering(
        input_parquet=load_data_task.outputs["dataset"]
    )
    feature_engineering_task.set_display_name("Feature-Engineering")
    
    preprocess_dataset_task = preprocess_dataset(
        engineered_dataset=feature_engineering_task.outputs["engineered_dataset"]
    )
    preprocess_dataset_task.set_display_name("Preprocessing")
    
    train_model_task = train_model(
        preprocessed_dataset=preprocess_dataset_task.outputs["preprocessed_dataset"]
    )
    train_model_task.set_display_name("Training")
    
    with kfp.dsl.If(train_model_task.outputs["roc_auc_out"] >= auc_threshold, name="model_ok"):
        # Aquí iría el despliegue (o simulado) si pasa el umbral.
        register_model_task = register_model(
            trained_model=train_model_task.outputs["model_artifact"],
            project_id=project_id,
            region=region,
            display_name=model_display_name,
            serving_image_uri=serving_image_uri,
        )
        register_model_task.set_display_name("Register-Model")
        
    with kfp.dsl.Else(name="model_not_ok"):
        # Falla explícitamente para dejar trazado
        # kfp.dsl.ContainerSpec(
        #     image="bash",
        #     command=["sh", "-c"],
        #     args=[f'echo "AUC < {auc_threshold}. Abortando registro." && exit 1']
        # )
        msg = f"AUC < {auc_threshold}. No se registra el modelo."
        not_ok = model_not_ok(msg=msg)
        not_ok.set_display_name("model_not_ok")