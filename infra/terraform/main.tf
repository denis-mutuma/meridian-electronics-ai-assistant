locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

module "ecr" {
  source = "./modules/ecr"
  name   = "${local.name_prefix}-backend"
}

module "openai_secret" {
  source = "./modules/secrets"
  name   = "${local.name_prefix}/openai-api-key"
  value  = var.openai_api_key
}

module "http_api_gateway" {
  source                 = "./modules/http_api_gateway"
  name_prefix            = local.name_prefix
  backend_https_url      = var.ecs_backend_https_url
  throttling_burst_limit = var.api_gateway_throttling_burst_limit
  throttling_rate_limit  = var.api_gateway_throttling_rate_limit
}

module "frontend_cloudfront" {
  source      = "./modules/frontend_cloudfront"
  name_prefix = local.name_prefix
}
