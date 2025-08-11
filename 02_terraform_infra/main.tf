# Habilitar APIs requeridas
resource "google_project_service" "services" {
  for_each = toset([
    "compute.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
  ])
  project                     = var.project_id
  service                     = each.key
  disable_on_destroy          = false
  disable_dependent_services  = false
}

# Service Account para pipelines/ejecuciones
resource "google_service_account" "pipeline" {
  account_id   = var.pipeline_sa_id
  display_name = "MLE Pipeline SA"
}

# Bucket GCS (staging / pipeline-root / datasets)
module "gcs_bucket" {
  source      = "./modules/gcs_bucket"
  name        = var.bucket_name
  location    = var.region
  labels      = local.labels
  force_unlock = true
}

# BigQuery Dataset
module "bq_dataset" {
  source      = "./modules/bq_dataset"
  dataset_id  = var.bq_dataset_id
  location    = var.location
  labels      = local.labels
}

# (Opcional) Vertex AI Endpoint vacío para despliegues posteriores
module "vertex_endpoint" {
  source     = "./modules/vertex_endpoint"
  create     = var.create_vertex_endpoint
  display_name = "endpoint-churn-${var.env}"
  location   = var.region
  labels     = local.labels
  depends_on = [google_project_service.services]
}