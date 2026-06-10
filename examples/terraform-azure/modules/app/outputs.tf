output "web_app_name" {
  value = azurerm_linux_web_app.main.name
}

output "service_plan_id" {
  value = azurerm_service_plan.main.id
}
