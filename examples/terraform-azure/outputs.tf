output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "web_app_name" {
  value = module.app.web_app_name
}

output "app_subnet_id" {
  value = module.network.app_subnet_id
}
