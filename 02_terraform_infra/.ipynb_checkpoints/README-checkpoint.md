# 02_terraform_infra – Terraform en GCP

Este módulo despliega:
- Bucket GCS (staging / datasets / pipeline-root)
- Dataset de BigQuery
- (Opcional) Endpoint de Vertex AI (vacío, listo para deploy de modelo)
- Service Account + IAM mínimos para ejecutar pipelines/Batch y leer/escribir datos

## Prerrequisitos
1. Proyecto con billing habilitado.
2. Autenticación local:
   - `gcloud auth application-default login`
   - o exportar `GOOGLE_APPLICATION_CREDENTIALS` a una key JSON con permisos de Owner/Editor temporalmente para el bootstrap.
3. Terraform >= 1.5, Provider Google >= 5.28.

## Variables
Ver `variables.tf` y ejemplo en `terraform.tfvars.example`.

## Pasos
```bash
cd 02_terraform_infra
cp terraform.tfvars.example terraform.tfvars
# Edita project_id, bucket_name, bq_dataset_id, etc.

terraform init
terraform plan
terraform apply -auto-approve