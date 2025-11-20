output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.vnet_rg.name
}

output "resource_group_id" {
  description = "ID of the resource group"
  value       = azurerm_resource_group.vnet_rg.id
}

output "vnet_name" {
  description = "Name of the Virtual Network"
  value       = azurerm_virtual_network.vnet.name
}

output "vnet_id" {
  description = "ID of the Virtual Network"
  value       = azurerm_virtual_network.vnet.id
}

output "vnet_address_space" {
  description = "Address space of the Virtual Network"
  value       = azurerm_virtual_network.vnet.address_space
}

output "subnet1_id" {
  description = "ID of the first subnet"
  value       = azurerm_subnet.subnet1.id
}

output "subnet1_name" {
  description = "Name of the first subnet"
  value       = azurerm_subnet.subnet1.name
}

output "subnet1_address_prefix" {
  description = "Address prefix of the first subnet"
  value       = azurerm_subnet.subnet1.address_prefixes[0]
}

output "subnet2_id" {
  description = "ID of the second subnet"
  value       = azurerm_subnet.subnet2.id
}

output "subnet2_name" {
  description = "Name of the second subnet"
  value       = azurerm_subnet.subnet2.name
}

output "subnet2_address_prefix" {
  description = "Address prefix of the second subnet"
  value       = azurerm_subnet.subnet2.address_prefixes[0]
}
