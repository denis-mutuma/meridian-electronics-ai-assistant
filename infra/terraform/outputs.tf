output "backend_ecr_repository_url" {
  value       = aws_ecr_repository.backend.repository_url
  description = "ECR repository URL for backend image"
}

output "openai_secret_arn" {
  value       = aws_secretsmanager_secret.openai_api_key.arn
  description = "Secret ARN for OpenAI API key"
}

output "jwt_secret_arn" {
  value       = aws_secretsmanager_secret.jwt_secret.arn
  description = "Secret ARN for JWT secret"
}
