locals {
  name_prefix                    = "${var.project_name}-${var.environment}"
  api_gateway_origin_domain_name = replace(module.http_api_gateway.api_endpoint, "https://", "")
}

module "lambda_backend" {
  source          = "./modules/lambda_backend"
  name_prefix     = local.name_prefix
  package_path    = var.lambda_package_path
  openai_api_key  = var.openai_api_key
  mcp_server_url  = var.mcp_server_url
  allowed_origins = var.lambda_allowed_origins

  memory_size        = var.lambda_memory_size
  timeout            = var.lambda_timeout
  log_retention_days = var.lambda_log_retention_days
}

module "http_api_gateway" {
  source               = "./modules/http_api_gateway"
  name_prefix          = local.name_prefix
  lambda_function_name = module.lambda_backend.function_name
  lambda_invoke_arn    = module.lambda_backend.invoke_arn

  throttling_burst_limit = var.api_gateway_throttling_burst_limit
  throttling_rate_limit  = var.api_gateway_throttling_rate_limit
}

module "frontend_cloudfront" {
  source                 = "./modules/frontend_cloudfront"
  name_prefix            = local.name_prefix
  api_origin_domain_name = local.api_gateway_origin_domain_name
}

module "github_oidc" {
  source      = "./modules/github_oidc"
  github_repo = var.github_repo

  s3_bucket_arn               = module.frontend_cloudfront.s3_bucket_arn
  cloudfront_distribution_arn = module.frontend_cloudfront.cloudfront_distribution_arn
  lambda_function_arn         = module.lambda_backend.function_arn

  # Set to false if a GitHub OIDC provider already exists in this account
  create_oidc_provider = var.create_github_oidc_provider
}
