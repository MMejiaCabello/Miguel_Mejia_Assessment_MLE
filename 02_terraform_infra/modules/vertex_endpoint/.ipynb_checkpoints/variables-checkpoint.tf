variable "create" { type = bool }
variable "display_name" { type = string }
variable "location" { type = string }
variable "labels" { type = map(string) default = {} }