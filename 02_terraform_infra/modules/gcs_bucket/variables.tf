variable "name" { type = string }
variable "location" { type = string }
variable "labels" { type = map(string) default = {} }
variable "force_unlock" { type = bool default = false }