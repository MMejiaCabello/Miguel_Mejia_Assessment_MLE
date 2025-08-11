output "pipeline_service_account" {
  value = local.pipeline_sa_email
}

output "gcs_bucket_name" {
  value = module.gcs_bucket.name
}

output "bq_dataset_id" {
  value = module.bq_dataset.dataset_id
}

output "vertex_endpoint_id" {
  value       = module.vertex_endpoint.endpoint_id
  description = "Vacío si create=false"
}