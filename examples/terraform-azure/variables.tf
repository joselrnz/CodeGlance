variable "project_name" {
  description = "Short project name used in Azure resource names."
  type        = string
  default     = "codeglance"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region."
  type        = string
  default     = "eastus"
}

variable "address_space" {
  description = "Virtual network CIDR blocks."
  type        = list(string)
  default     = ["10.42.0.0/16"]
}
