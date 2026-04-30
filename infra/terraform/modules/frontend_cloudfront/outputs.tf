output "s3_bucket_id" {
  value       = aws_s3_bucket.site.id
  description = "S3 bucket name (use for aws s3 sync in CI)"
}

output "cloudfront_distribution_id" {
  value       = aws_cloudfront_distribution.site.id
  description = "CloudFront distribution id (for cache invalidation)"
}

output "cloudfront_domain_name" {
  value       = aws_cloudfront_distribution.site.domain_name
  description = "CloudFront domain (*.cloudfront.net)"
}

output "frontend_url" {
  value       = "https://${aws_cloudfront_distribution.site.domain_name}"
  description = "HTTPS URL for the static frontend"
}
