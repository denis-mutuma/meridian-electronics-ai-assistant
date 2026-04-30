output "backend_ecr_repository_url" {
  value       = module.ecr.repository_url
  description = "ECR repository URL for backend image"
}

output "backend_service_url" {
  value       = module.apprunner.service_url
  description = "Public URL for the App Runner backend service"
}

output "frontend_domain" {
  value       = module.amplify.default_domain
  description = "Amplify default domain"
}

output "openai_secret_arn" {
  value       = module.openai_secret.secret_arn
  description = "Secret ARN for OpenAI API key"
}

output "jwt_secret_arn" {
  value       = module.jwt_secret.secret_arn
  description = "Secret ARN for JWT secret"
}
