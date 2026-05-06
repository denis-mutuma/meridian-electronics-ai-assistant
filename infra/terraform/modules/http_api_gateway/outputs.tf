output "api_id" {
  value       = aws_apigatewayv2_api.this.id
  description = "HTTP API id"
}

output "api_endpoint" {
  value       = aws_apigatewayv2_api.this.api_endpoint
  description = "Invoke URL base (no trailing slash). CloudFront forwards /api/* here."
}

output "execution_arn" {
  value       = aws_apigatewayv2_api.this.execution_arn
  description = "Execution ARN for IAM policies"
}
