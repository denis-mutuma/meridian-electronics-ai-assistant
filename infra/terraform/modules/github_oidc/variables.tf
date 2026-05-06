variable "role_name" {
  description = "Name of the IAM role for GitHub Actions"
  type        = string
  default     = "meridian-electronics-github-actions"
}

variable "github_repo" {
  description = "GitHub repository allowed to assume this role, in owner/name format"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the frontend S3 bucket"
  type        = string
}

variable "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  type        = string
}

variable "lambda_function_arn" {
  description = "ARN of the backend Lambda function"
  type        = string
}

variable "create_oidc_provider" {
  description = "Set to false if a GitHub OIDC provider already exists in this AWS account"
  type        = bool
  default     = true
}
