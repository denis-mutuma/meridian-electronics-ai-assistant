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

module "apprunner" {
  source           = "./modules/apprunner"
  service_name     = "${local.name_prefix}-backend"
  image_identifier = var.backend_image_identifier
  environment = {
    OPENAI_MODEL    = "gpt-4o-mini"
    MCP_SERVER_URL  = var.mcp_server_url
    JWT_SECRET      = var.jwt_secret
    OPENAI_API_KEY  = var.openai_api_key
    ALLOWED_ORIGINS = "*"
    BACKEND_HOST    = "0.0.0.0"
    BACKEND_PORT    = "8000"
  }
}

module "amplify" {
  source       = "./modules/amplify"
  app_name     = "${local.name_prefix}-frontend"
  repository   = var.github_repository
  github_token = var.github_token
  branch_name  = var.git_branch
  environment = {
    NEXT_PUBLIC_API_BASE_URL = "https://${module.apprunner.service_url}"
  }
}
