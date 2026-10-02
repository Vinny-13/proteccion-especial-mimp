resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    project    = "mimp-proteccion-especial"
    managed_by = "terraform"
  }
}

resource "azurerm_postgresql_flexible_server" "this" {
  name                   = var.server_name
  resource_group_name    = azurerm_resource_group.this.name
  location               = azurerm_resource_group.this.location
  version                = "16"
  administrator_login    = var.db_admin_username
  administrator_password = var.db_admin_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  backup_retention_days  = 7

  public_network_access_enabled = true

  tags = {
    project    = "mimp-proteccion-especial"
    managed_by = "terraform"
  }
}

resource "azurerm_postgresql_flexible_server_database" "this" {
  name      = var.database_name
  server_id = azurerm_postgresql_flexible_server.this.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Azure services need this rule for the workflow and optional platform tools.
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.this.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "github_actions" {
  count            = var.github_actions_ip == "0.0.0.0" ? 0 : 1
  name             = "GitHubActionsRunner"
  server_id        = azurerm_postgresql_flexible_server.this.id
  start_ip_address = var.github_actions_ip
  end_ip_address   = var.github_actions_ip
}
