resource "google_storage_bucket" "this" {
  name          = var.name
  location      = var.location
  force_destroy = true

  uniform_bucket_level_access = true
  versioning { enabled = true }

  lifecycle_rule {
    action { type = "Delete" }
    condition {
      age = 45
    }
  }

  labels = var.labels
}