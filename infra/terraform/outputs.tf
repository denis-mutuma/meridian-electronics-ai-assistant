output "backend_ecr_repository_url" {
  value       = module.ecr.repository_url
  description = "ECR repository URL for backend image"
}

output "api_gateway_invoke_url" {
  value       = module.http_api_gateway.api_endpoint
  description = "Public HTTP API invoke URL (set ECS / GitHub NEXT_PUBLIC_API_BASE_URL to this)"
}

output "api_gateway_id" {
  value       = module.http_api_gateway.api_id
  description = "HTTP API Gateway id"
}

output "frontend_s3_bucket" {
  value       = module.frontend_cloudfront.s3_bucket_id
  description = "S3 bucket for static frontend (GitHub var FRONTEND_S3_BUCKET)"
}

output "cloudfront_distribution_id" {
  value       = module.frontend_cloudfront.cloudfront_distribution_id
  description = "CloudFront distribution id (GitHub var CLOUDFRONT_DISTRIBUTION_ID)"
}

output "cloudfront_domain_name" {
  value       = module.frontend_cloudfront.cloudfront_domain_name
  description = "CloudFront *.cloudfront.net hostname"
}

output "frontend_url" {
  value       = module.frontend_cloudfront.frontend_url
  description = "HTTPS URL for the UI (CloudFront)"
}

output "frontend_origin_https" {
  value       = module.frontend_cloudfront.frontend_url
  description = "Same as frontend_url — set ECS ALLOWED_ORIGINS / GitHub var to this for CORS"
}

output "openai_secret_arn" {
  value       = module.openai_secret.secret_arn
  description = "Secret ARN for OpenAI API key (ECS task definition secrets.valueFrom)"
}
