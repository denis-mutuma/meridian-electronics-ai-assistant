variable "name_prefix" {
  description = "Prefix for API Gateway resource names"
  type        = string
}

variable "backend_https_url" {
  description = "HTTPS origin for ECS (ALB listener URL), no trailing slash, e.g. https://my-alb.us-east-1.elb.amazonaws.com"
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
