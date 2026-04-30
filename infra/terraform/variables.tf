variable "project_name" {
  description = "Project slug used for naming"
  type        = string
  default     = "meridian-electronics-ai-assistant"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "openai_api_key" {
  description = "OpenAI API key (stored in Secrets Manager for ECS to reference)"
  type        = string
  sensitive   = true
}

variable "ecs_backend_https_url" {
  description = "Public HTTPS URL of the ECS load balancer (ALB) in front of the FastAPI service. No trailing slash. API Gateway HTTP proxies to this origin."
  type        = string
  
  validation {
    condition = (
      startswith(var.ecs_backend_https_url, "https://") &&
      !endswith(var.ecs_backend_https_url, "/") &&
      length(regexall("execute-api\\.", var.ecs_backend_https_url)) == 0 &&
      length(regexall("elb\\.amazonaws\\.com$", var.ecs_backend_https_url)) > 0
    )
    error_message = "ecs_backend_https_url must be the HTTPS ALB origin, end with elb.amazonaws.com, must not have a trailing slash, and must not point to an execute-api URL."
  }
}

variable "api_gateway_throttling_burst_limit" {
  description = "HTTP API stage burst limit (default route)"
  type        = number
  default     = 100
}

variable "api_gateway_throttling_rate_limit" {
  description = "HTTP API stage steady-state requests per second (default route)"
  type        = number
  default     = 50
}
