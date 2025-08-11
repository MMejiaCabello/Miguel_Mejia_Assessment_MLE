from kfp.dsl import component, Input, Model

@component(
    base_image="python:3.10",
    packages_to_install=[
        "google-cloud-aiplatform==1.59.0"
    ]
)
def register_model(
    trained_model: Input[Model],
    project_id: str,
    region: str,
    display_name: str = "churn-xgb",
    serving_image_uri: str = "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-7:latest",
) -> str:
    """
    Sube el modelo al Model Registry usando el directorio del artefacto como artifact_uri.
    Retorna el resource name del Model.
    """
    from google.cloud import aiplatform

    aiplatform.init(
        project=project_id,
        location=region
    )
    
    artifact_uri = trained_model.path  # carpeta con model.json

    print(f"[INFO] Registrando modelo desde: {artifact_uri}")
    model = aiplatform.Model.upload(
        display_name=display_name,
        artifact_uri=artifact_uri,
        serving_container_image_uri=serving_image_uri,
        labels={"usecase":"churn","stage":"dev"},
        description="XGBoost churn entrenado vía Vertex Pipelines"
    )
    model.wait()
    print(f"[INFO] Registrado: {model.resource_name}")
    return model.resource_name
