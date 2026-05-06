output "api_gateway_invoke_url" {
  value       = module.http_api_gateway.api_endpoint
  description = "Public HTTP API invoke URL. CloudFront forwards /api/* here."
}

output "frontend_s3_bucket" {
  value       = module.frontend_cloudfront.s3_bucket_id
  description = "S3 bucket for static frontend (GitHub var FRONTEND_S3_BUCKET)"
}

output "cloudfront_distribution_id" {
  value       = module.frontend_cloudfront.cloudfront_distribution_id
  description = "CloudFront distribution id (GitHub var CLOUDFRONT_DISTRIBUTION_ID)"
}

output "frontend_url" {
  value       = module.frontend_cloudfront.frontend_url
  description = "HTTPS URL for the UI (CloudFront)"
}

output "lambda_function_name" {
  value       = module.lambda_backend.function_name
  description = "Backend Lambda function name (GitHub var BACKEND_LAMBDA_FUNCTION_NAME)"
}
