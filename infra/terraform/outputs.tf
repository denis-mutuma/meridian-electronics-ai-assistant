output "backend_ecr_repository_url" {
  value       = module.ecr.repository_url
  description = "ECR repository URL for backend image"
}

output "api_gateway_invoke_url" {
  value       = module.http_api_gateway.api_endpoint
  description = "Public HTTP API invoke URL (use for NEXT_PUBLIC_API_BASE_URL / clients)"
}

output "api_gateway_id" {
  value       = module.http_api_gateway.api_id
  description = "HTTP API Gateway id"
}

output "amplify_origin_https" {
  value       = "https://${var.git_branch}.${module.amplify.default_domain}"
  description = "Amplify hosted UI origin — set GitHub variable ALLOWED_ORIGINS to this (and any custom domains) for ECS backend CORS"
}

output "frontend_domain" {
  value       = module.amplify.default_domain
  description = "Amplify default domain (suffix for branch URLs)"
}

output "frontend_app_id" {
  value       = module.amplify.app_id
  description = "Amplify app ID"
}

output "openai_secret_arn" {
  value       = module.openai_secret.secret_arn
  description = "Secret ARN for OpenAI API key (ECS task definition secrets.valueFrom)"
}

output "jwt_secret_arn" {
  value       = module.jwt_secret.secret_arn
  description = "Secret ARN for JWT signing secret (ECS task definition secrets.valueFrom)"
}
