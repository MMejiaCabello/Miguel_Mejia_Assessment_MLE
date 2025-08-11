output "endpoint_id" {
  value = length(google_vertex_ai_endpoint.this) > 0 ? google_vertex_ai_endpoint.this[0].name : null
}