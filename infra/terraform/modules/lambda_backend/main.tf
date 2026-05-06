resource "aws_iam_role" "lambda" {
  name = "${var.name_prefix}-backend-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "basic_execution" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.name_prefix}-backend"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "backend" {
  function_name    = "${var.name_prefix}-backend"
  role             = aws_iam_role.lambda.arn
  handler          = "app.lambda_handler.handler"
  runtime          = "python3.12"
  filename         = var.package_path
  source_code_hash = filebase64sha256(var.package_path)
  memory_size      = var.memory_size
  timeout          = var.timeout

  environment {
    variables = {
      ALLOWED_ORIGINS = var.allowed_origins
      MCP_SERVER_URL  = var.mcp_server_url
      OPENAI_API_KEY  = var.openai_api_key
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy_attachment.basic_execution,
  ]
}
