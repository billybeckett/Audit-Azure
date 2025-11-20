terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# Create or use existing resource group
resource "azurerm_resource_group" "vnet_rg" {
  name     = var.resource_group_name
  location = var.location
}

# Create Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  location            = azurerm_resource_group.vnet_rg.location
  resource_group_name = azurerm_resource_group.vnet_rg.name
  address_space       = var.vnet_address_space

  tags = var.tags
}

# Create Subnet 1
resource "azurerm_subnet" "subnet1" {
  name                 = var.subnet1_name
  resource_group_name  = azurerm_resource_group.vnet_rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet1_address_prefix]

  # Optional: Add service endpoints if needed
  # service_endpoints = ["Microsoft.Storage", "Microsoft.Sql"]
}

# Create Subnet 2
resource "azurerm_subnet" "subnet2" {
  name                 = var.subnet2_name
  resource_group_name  = azurerm_resource_group.vnet_rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet2_address_prefix]

  # Optional: Add service endpoints if needed
  # service_endpoints = ["Microsoft.Storage", "Microsoft.Sql"]
}
