project_id      = "dev-farma-analytics-workspace"
region          = "us-central1"
location        = "US"
bucket_name     = "assessment-mle"
bq_dataset_id   = "bi_churn_assessment"
env             = "dev"
create_vertex_endpoint = true
pipeline_sa_id  = "mle-pipeline-sa"
labels = {
  owner = "Miguel Mejia"
}