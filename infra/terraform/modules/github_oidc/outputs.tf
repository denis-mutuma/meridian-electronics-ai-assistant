output "role_arn" {
  value       = aws_iam_role.github_actions.arn
  description = "ARN of the GitHub Actions IAM role (set AWS_ROLE_ARN in the GitHub Environment if you override the default)"
}

output "role_name" {
  value       = aws_iam_role.github_actions.name
  description = "Name of the GitHub Actions IAM role"
}
