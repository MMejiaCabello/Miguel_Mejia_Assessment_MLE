# Permite activar/desactivar el recurso limpiamente
resource "google_vertex_ai_endpoint" "this" {
  count        = var.create ? 1 : 0
  display_name = var.display_name
  location     = var.location
  labels       = var.labels
}