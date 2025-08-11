variable "project_id" {
  description = "ID del proyecto de GCP"
  type        = string
}

variable "region" {
  description = "Región para recursos regionales (p.ej., us-central1)"
  type        = string
  default     = "us-central1"
}

variable "location" {
  description = "Ubicación para BigQuery y Vertex AI (p.ej., US o us-central1)"
  type        = string
  default     = "US"
}

variable "bucket_name" {
  description = "Nombre del bucket GCS"
  type        = string
}

variable "bq_dataset_id" {
  description = "ID del dataset de BigQuery"
  type        = string
}

variable "env" {
  description = "Etiqueta de entorno (dev, qa, prd)"
  type        = string
  default     = "dev"
}

variable "create_vertex_endpoint" {
  description = "Si true, crea un Endpoint vacío en Vertex AI"
  type        = bool
  default     = true
}

variable "pipeline_sa_id" {
  description = "ID del Service Account (sin dominio) para pipelines/ejecuciones"
  type        = string
  default     = "mle-pipeline-sa"
}

variable "labels" {
  description = "Etiquetas comunes"
  type        = map(string)
  default     = {}
}