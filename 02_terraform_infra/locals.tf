locals {
  labels = merge({
    env       = var.env
    managedby = "terraform"
    app       = "assessment-mle"
  }, var.labels)

  pipeline_sa_email = "${var.pipeline_sa_id}@${var.project_id}.iam.gserviceaccount.com"
}