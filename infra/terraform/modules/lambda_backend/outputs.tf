output "function_name" {
  value       = aws_lambda_function.backend.function_name
  description = "Lambda backend function name"
}

output "function_arn" {
  value       = aws_lambda_function.backend.arn
  description = "Lambda backend function ARN"
}

output "invoke_arn" {
  value       = aws_lambda_function.backend.invoke_arn
  description = "Lambda backend invoke ARN for API Gateway integration"
}
