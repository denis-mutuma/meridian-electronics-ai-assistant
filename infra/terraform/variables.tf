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
  description = "OpenAI API key injected into the backend Lambda"
  type        = string
  sensitive   = true
}

variable "mcp_server_url" {
  description = "MCP server that holds customer and order data"
  type        = string
  default     = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"
}

variable "lambda_package_path" {
  description = "Path to the backend Lambda deployment zip. Run scripts/build_lambda_package.sh before terraform apply."
  type        = string
  default     = "../../build/backend-lambda.zip"
}

variable "lambda_allowed_origins" {
  description = "Comma-separated CORS origins for direct API access. Same-origin CloudFront /api calls do not require CORS."
  type        = string
  default     = "http://localhost:3000"
}

variable "lambda_memory_size" {
  description = "Backend Lambda memory size in MB"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Backend Lambda timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_log_retention_days" {
  description = "Backend Lambda CloudWatch log retention in days"
  type        = number
  default     = 7
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

variable "github_repo" {
  description = "GitHub repository allowed to assume the CI/CD role, in owner/name format"
  type        = string
  default     = "denis-mutuma/meridian-electronics-ai-assistant"
}

variable "create_github_oidc_provider" {
  description = "Set to false if a GitHub Actions OIDC provider already exists in this AWS account"
  type        = bool
  default     = true
}
