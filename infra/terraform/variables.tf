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

variable "backend_image_identifier" {
  description = "Backend image URI for App Runner"
  type        = string
}

variable "github_repository" {
  description = "GitHub repository URL for Amplify"
  type        = string
}

variable "github_token" {
  description = "GitHub personal access token for Amplify webhook"
  type        = string
  sensitive   = true
}

variable "git_branch" {
  description = "Branch for Amplify deployment"
  type        = string
  default     = "main"
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT signing secret"
  type        = string
  sensitive   = true
}

variable "mcp_server_url" {
  description = "MCP server endpoint"
  type        = string
  default     = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"
}
