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
  backend_https_url      = "http://${module.alb.alb_dns_name}"
  throttling_burst_limit = var.api_gateway_throttling_burst_limit
  throttling_rate_limit  = var.api_gateway_throttling_rate_limit
}

module "frontend_cloudfront" {
  source      = "./modules/frontend_cloudfront"
  name_prefix = local.name_prefix
}

module "github_oidc" {
  source      = "./modules/github_oidc"
  github_repo = var.github_repo

  ecr_repository_arns         = [module.ecr.repository_arn]
  s3_bucket_arn               = module.frontend_cloudfront.s3_bucket_arn
  cloudfront_distribution_arn = module.frontend_cloudfront.cloudfront_distribution_arn

  # Set to false if a GitHub OIDC provider already exists in this account
  create_oidc_provider = var.create_github_oidc_provider
}

module "alb" {
  source              = "./modules/alb"
  name_prefix         = "meridian-backend"
  alb_sg_name         = "meridian-alb-sg"
  alb_sg_description  = "ALB SG for Meridian backend"
  vpc_id              = "vpc-04fd829243be5012c"
  subnet_ids          = ["subnet-0fb1fc175c0336c94", "subnet-025b8b5b524988654"]
  ecs_sg_id           = "sg-05b341751eeb224bb"
}
