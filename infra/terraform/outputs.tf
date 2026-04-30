output "backend_ecr_repository_url" {
  value       = module.ecr.repository_url
  description = "ECR repository URL for backend image"
}

output "backend_service_url" {
  value       = module.apprunner.service_url
  description = "Public URL for the App Runner backend service"
}

output "backend_service_arn" {
  value       = module.apprunner.service_arn
  description = "App Runner backend service ARN"
}

output "frontend_domain" {
  value       = module.amplify.default_domain
  description = "Amplify default domain"
}

output "frontend_app_id" {
  value       = module.amplify.app_id
  description = "Amplify app ID"
}

output "openai_secret_arn" {
  value       = module.openai_secret.secret_arn
  description = "Secret ARN for OpenAI API key"
}

output "jwt_secret_arn" {
  value       = module.jwt_secret.secret_arn
  description = "Secret ARN for JWT secret"
}
