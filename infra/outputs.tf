output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "server_name" {
  value = azurerm_postgresql_flexible_server.this.name
}

output "server_fqdn" {
  value = azurerm_postgresql_flexible_server.this.fqdn
}

output "database_name" {
  value = azurerm_postgresql_flexible_server_database.this.name
}

output "jdbc_url" {
  value = "jdbc:postgresql://${azurerm_postgresql_flexible_server.this.fqdn}:5432/${azurerm_postgresql_flexible_server_database.this.name}?sslmode=require"
}
