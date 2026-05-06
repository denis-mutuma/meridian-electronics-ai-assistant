variable "name_prefix" {
  description = "Prefix for Lambda resource names"
  type        = string
}

variable "package_path" {
  description = "Path to the Lambda deployment zip"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key injected into Lambda"
  type        = string
  sensitive   = true
}

variable "mcp_server_url" {
  description = "MCP server URL used by the backend"
  type        = string
}

variable "allowed_origins" {
  description = "Comma-separated CORS origins for direct API access"
  type        = string
}

variable "memory_size" {
  description = "Lambda memory size in MB"
  type        = number
  default     = 512
}

variable "timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}
