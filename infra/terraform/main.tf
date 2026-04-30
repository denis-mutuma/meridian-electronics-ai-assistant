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

module "jwt_secret" {
  source = "./modules/secrets"
  name   = "${local.name_prefix}/jwt-secret"
  value  = var.jwt_secret
}

module "http_api_gateway" {
  source                 = "./modules/http_api_gateway"
  name_prefix            = local.name_prefix
  backend_https_url      = var.ecs_backend_https_url
  throttling_burst_limit = var.api_gateway_throttling_burst_limit
  throttling_rate_limit  = var.api_gateway_throttling_rate_limit
}

module "amplify" {
  source       = "./modules/amplify"
  app_name     = "${local.name_prefix}-frontend"
  repository   = var.github_repository
  github_token = var.github_token
  branch_name  = var.git_branch
  environment = {
    NEXT_PUBLIC_API_BASE_URL = module.http_api_gateway.api_endpoint
  }
}
