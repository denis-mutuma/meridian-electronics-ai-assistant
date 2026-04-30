variable "name_prefix" {
  description = "Prefix for resource names (S3 bucket includes random suffix for global uniqueness)"
  type        = string
}

variable "price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}
