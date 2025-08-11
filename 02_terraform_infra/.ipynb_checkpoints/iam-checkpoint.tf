# Permisos mínimos para la SA sobre el proyecto (JobUser y Vertex User)
resource "google_project_iam_member" "sa_bq_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${local.pipeline_sa_email}"
}

resource "google_project_iam_member" "sa_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${local.pipeline_sa_email}"
}

# Acceso al bucket (Object Admin)
resource "google_storage_bucket_iam_member" "sa_bucket_obj_admin" {
  bucket = module.gcs_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${local.pipeline_sa_email}"
}

# Acceso al dataset (Data Editor)
resource "google_bigquery_dataset_iam_member" "sa_bq_editor" {
  dataset_id = module.bq_dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${local.pipeline_sa_email}"
}