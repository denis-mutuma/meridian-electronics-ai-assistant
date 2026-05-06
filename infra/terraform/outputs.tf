output "api_gateway_invoke_url" {
  value       = module.http_api_gateway.api_endpoint
  description = "Public HTTP API invoke URL. CloudFront forwards /api/* here."
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

output "github_actions_role_arn" {
  value       = module.github_oidc.role_arn
  description = "IAM role ARN for GitHub Actions OIDC (set AWS_ROLE_ARN GitHub var if you override the default)"
}

output "lambda_function_name" {
  value       = module.lambda_backend.function_name
  description = "Backend Lambda function name (GitHub var BACKEND_LAMBDA_FUNCTION_NAME)"
}
