variable "name_prefix" {
  description = "Prefix for API Gateway resource names"
  type        = string
}

variable "lambda_function_name" {
  description = "Lambda backend function name"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Lambda backend invoke ARN"
  type        = string
}

variable "throttling_burst_limit" {
  description = "API Gateway stage default route burst limit"
  type        = number
  default     = 100
}

variable "throttling_rate_limit" {
  description = "API Gateway stage default route steady-state RPS limit"
  type        = number
  default     = 50
}
