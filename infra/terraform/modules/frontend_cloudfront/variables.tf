variable "name_prefix" {
  description = "Prefix for resource names (S3 bucket includes random suffix for global uniqueness)"
  type        = string
}

variable "price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}

variable "api_origin_domain_name" {
  description = "API Gateway domain name for /api/* requests, without protocol"
  type        = string
  default     = ""
}
