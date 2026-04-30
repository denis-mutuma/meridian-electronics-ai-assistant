resource "aws_amplify_app" "this" {
  name         = var.app_name
  repository   = var.repository
  access_token = var.github_token

  environment_variables = var.environment

  build_spec = <<-EOT
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/.next
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
EOT
}

resource "aws_amplify_branch" "this" {
  app_id      = aws_amplify_app.this.id
  branch_name = var.branch_name
}
