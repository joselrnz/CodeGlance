output "app_subnet_id" {
  value = azurerm_subnet.app.id
}

output "virtual_network_name" {
  value = azurerm_virtual_network.main.name
}
