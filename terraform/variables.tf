variable "subscription_id" {
  description = "Azure Subscription ID where resources will be created"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group (will be created if it doesn't exist)"
  type        = string
  default     = "rg-networking"
}

variable "location" {
  description = "Azure region where resources will be created"
  type        = string
  default     = "eastus"
}

variable "vnet_name" {
  description = "Name of the Virtual Network"
  type        = string
  default     = "vnet-terraform"
}

variable "vnet_address_space" {
  description = "Address space for the Virtual Network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet1_name" {
  description = "Name of the first subnet"
  type        = string
  default     = "subnet-web"
}

variable "subnet1_address_prefix" {
  description = "Address prefix for the first subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "subnet2_name" {
  description = "Name of the second subnet"
  type        = string
  default     = "subnet-app"
}

variable "subnet2_address_prefix" {
  description = "Address prefix for the second subnet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Environment = "Development"
    ManagedBy   = "Terraform"
  }
}
