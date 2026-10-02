variable "resource_group_name" {
  description = "Grupo de recursos de Azure para la solución."
  type        = string
  default     = "rg-mimp-proteccion"
}

variable "location" {
  description = "Región de Azure para PostgreSQL."
  type        = string
  default     = "eastus"
}

variable "server_name" {
  description = "Nombre globalmente único del servidor PostgreSQL; solo minúsculas, números y guiones."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]{3,63}$", var.server_name))
    error_message = "server_name debe tener entre 3 y 63 caracteres usando minúsculas, números y guiones."
  }
}

variable "database_name" {
  description = "Base de datos de la solución."
  type        = string
  default     = "mimp_proteccion"
}

variable "db_admin_username" {
  description = "Usuario administrador de PostgreSQL."
  type        = string
  default     = "mimpadmin"
}

variable "db_admin_password" {
  description = "Contraseña del administrador; se entrega por secret en GitHub Actions."
  type        = string
  sensitive   = true
}

variable "github_actions_ip" {
  description = "IP pública temporal del runner de GitHub Actions. 0.0.0.0 omite la regla temporal."
  type        = string
  default     = "0.0.0.0"
}
